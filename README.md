# 🦖 Babel Zilla — Neural Localization Engine

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![GCP](https://img.shields.io/badge/GCP-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)](https://cloud.google.com/)

Motor de localización semántica de alto rendimiento para aplicaciones modernas. Traduce payloads `i18n` preservando variables `{{user}}`, etiquetas HTML y tono de marca, con caché relacional para respuesta `0ms` en hits.

> **Stack:** `FastAPI (Python 3.12) + Gemini 2.5 Flash (Vertex AI) + PostgreSQL (Neon) + Docker + Cloud Run`

---

## ✨ Características

- **Traducción con contexto:** respeta `target_lang, tone, culture, context_hint` (ej. `Spanish / Casual / Peruvian`)
- **Preservación de lógica:** no rompe placeholders `{{var}}` ni HTML
- **Caché inteligente:** `hash + perfil` en PostgreSQL (`JSONB`) — `from_cache: true` en hits
- **Multilenguaje:** ES, EN, PT, FR, JA, KO, ZH y extensible por perfil
- **API batch:** traduce 1..N textos en una sola petición

## 🏗️ Arquitectura

```mermaid
graph LR
  Client --> FastAPI
  FastAPI --> Cache[(PostgreSQL - Neon)]
  FastAPI -->|miss| VertexAI[Vertex AI - Gemini 2.5 Flash]
  VertexAI --> FastAPI
  FastAPI --> DB[(tablas: textos_originales, perfiles, traducciones)]
  FastAPI --> Client
```

| Componente | Tecnología | Responsabilidad |
| :--- | :--- | :--- |
| API | FastAPI + Uvicorn | Endpoints asíncronos, validación `Pydantic`, `OpenAPI /docs` |
| Reasoning | Vertex AI (Gemini 2.5 Flash) | Traducción semántica con prompt por tono/cultura |
| Persistencia | PostgreSQL (Neon) | Caché `hash_id + perfil` y trazabilidad |
| Infra | Docker + Cloud Run | Deploy serverless con auto-escalado |
| CI/CD | Cloud Build + GitHub | Build y deploy en push a `main` |

## 📦 Estructura

```
.
├── src/
│   ├── main.py        # FastAPI app + POST /translate
│   ├── engine.py      # Cliente Vertex AI
│   ├── crud.py        # get_bulk_cached_translations / save_translation
│   ├── database.py    # Conexión psycopg2 + test_connection
│   ├── schemas.py     # Pydantic TranslationRequest/Response
│   └── config.py      # settings desde .env
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🚀 Inicio rápido con Docker (recomendado)

```bash
# 1. Variables de entorno
cp .env.example .env
# editar DATABASE_URL, GOOGLE_PROJECT_ID, GOOGLE_LOCATION

# 2. Credencial GCP (si usas Vertex AI real)
# colocar service-account.json y mapear en docker-compose.yml

# 3. Levantar
docker-compose up --build -d

# API en http://localhost:8000  |  Docs en http://localhost:8000/docs
```

## 🔧 Configuración manual

**Requisitos:** `Python 3.12+`, `PostgreSQL 14+`, `GCP` con `Vertex AI API` habilitada.

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn src.main:app --reload --port 8000
```

**.env**

```env
DATABASE_URL=postgresql://user:pass@host:5432/babelzilla
GOOGLE_PROJECT_ID=tu-proyecto-gcp
GOOGLE_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json
```

**Inicialización DB (Neon/local):**

```sql
CREATE TABLE IF NOT EXISTS textos_originales (
    id SERIAL PRIMARY KEY,
    hash_id VARCHAR(255) UNIQUE NOT NULL,
    contenido_original TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS perfiles_localizacion (
    id SERIAL PRIMARY KEY,
    idioma_destino VARCHAR(50) NOT NULL,
    tono VARCHAR(50) NOT NULL,
    contexto_cultural VARCHAR(100) NOT NULL,
    UNIQUE(idioma_destino, tono, contexto_cultural)
);
CREATE TABLE IF NOT EXISTS traducciones (
    id SERIAL PRIMARY KEY,
    id_original INTEGER REFERENCES textos_originales(id) ON DELETE CASCADE,
    id_perfil INTEGER REFERENCES perfiles_localizacion(id) ON DELETE CASCADE,
    texto_traducido TEXT NOT NULL
);
```

## 📡 Uso de la API

### `POST /translate`

**Request (payload mode — recomendado para i18n):**

```json
{
  "payload": { "WELCOME": "Welcome back, {{user}}!" },
  "target_lang": "Spanish",
  "tone": "Casual",
  "culture": "Peruvian"
}
```

**Request (batch mode):**

```json
{
  "texts": ["Hello", "Good morning"],
  "target_lang": "Spanish",
  "tone": "Formal",
  "culture": "Neutral"
}
```

**Response:**

```json
{
  "translated_payload": { "WELCOME": "¡Qué bueno verte de nuevo, {{user}}!" },
  "from_cache": false
}
```

```json
{
  "translations": ["Hola", "Buenos días"],
  "from_cache": true
}
```

Otros endpoints: `GET /` health, `GET /docs` Swagger, `GET /test-brain` test Vertex AI.

## ⚡ Performance

- `cache hit`: `~2-5ms` (PostgreSQL `hash` lookup)
- `cache miss`: `~400-900ms` (Gemini 2.5 Flash batch 1-10 textos) + persistencia
- Batch reduce costo y latencia vs 1 request por texto

## 🛡️ Seguridad

- `.env` y `service-account.json` ignorados por `.gitignore`
- Historial limpiado en `v2.1` — sin credenciales en Git
- Validación `Pydantic` y `CORS` configurable en `src/main.py`

## 🗺️ Roadmap

- [ ] `tests` con `pytest + Testcontainers` + `CI` en GitHub Actions
- [ ] Rate limiting + métricas `Prometheus`
- [ ] Perfil `tone` por tenant

## 📄 Licencia

MIT — ver `LICENSE`.

---

**Babel Zilla Engine** — *Traduciendo el futuro, una frase a la vez.*
