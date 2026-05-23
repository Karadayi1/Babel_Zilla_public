<div align="center">

# 🦖 BABEL-ZILLA : NEURAL LOCALIZATION ENGINE (v2.1)

[![Python 3.12](https://img.shields.io/badge/Python-3.12-00F?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Vertex AI](https://img.shields.io/badge/Vertex_AI-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)](https://cloud.google.com/vertex-ai)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

*Motor de traducción semántico de alto rendimiento, optimizado para la nube y diseñado para preservar la lógica de negocio.*

---
</div>

## 🌌 Mi Visión
He diseñado **Babel-Zilla** para ser algo más que un simple traductor. Mi objetivo es resolver la localización de aplicaciones modernas mediante **IA Generativa (Gemini 2.5 Flash)**. Mi motor no solo traduce palabras; entiende el contexto cultural, respeta el tono de voz de la marca y garantiza que la lógica del software (variables y etiquetas HTML) permanezca intacta.

He escalado el motor para soportar una **audiencia global**, integrando idiomas como **Chino, Coreano, Japonés, Francés y Portugués**. El sistema asegura que el parámetro psicológico del "tono" dicte con precisión los matices lingüísticos de cada región.

Combinando la potencia de Google Cloud con una **capa de persistencia en Neon (PostgreSQL)**, he logrado que mi sistema ofrezca respuestas instantáneas (0ms) mediante una caché inteligente, reduciendo costos y latencia al mínimo, incluso bajo alta carga de peticiones transculturales.

---

## 🛠️ Mi Arquitectura de Producción

He estructurado este microservicio para ser escalable y seguro:

| Componente | Tecnología | Mi Rol |
| :--- | :--- | :--- |
| **API Framework** | FastAPI | Interfaz asíncrona de alto rendimiento. |
| **Reasoning Engine**| Vertex AI (Gemini 2.5 Flash) | Mi "cerebro" para razonamiento semántico. |
| **Memory Bank** | Neon PostgreSQL | Mi "memoria" persistente para caché y perfiles. |
| **Cloud Deployment**| Google Cloud Run | Mi infraestructura serverless con escalado automático. |
| **CI/CD** | Cloud Build + GitHub | Despliegue automático con cada cambio en mi código. |

---

## 🛡️ Seguridad y Limpieza
En esta versión 2.1, he realizado un proceso de **limpieza profunda del historial de Git** para asegurar que ninguna credencial quede expuesta, reiniciando el repositorio con un archivo `.gitignore` robusto y profesional. La seguridad es mi prioridad.

---

## 🚀 Instalación y Configuración

### 🐳 Despliegue Rápido con Docker (Recomendado)

He configurado este proyecto para que puedas levantarlo en segundos usando contenedores. Esto iniciará la base de datos PostgreSQL local, la API principal y el backend secundario automáticamente:

1. Crea tu archivo `.env` en la raíz basándote en la estructura que detallo más abajo.
2. Coloca tu archivo de credenciales de Google Cloud (`.json`) en la ruta configurada en los volúmenes de tu `docker-compose.yml`.
3. Ejecuta el entorno completo en la terminal:
   ```bash
   docker-compose up --build -d
   ```
¡Listo! La API estará escuchando peticiones en `http://localhost:8000`.

---

### 🛠️ Configuración Manual

#### 1. Requisitos Previos
- Cuenta en Google Cloud con la API de Vertex AI habilitada.
- Base de datos PostgreSQL (Recomiendo **Neon.tech** para despliegue manual en la nube).

#### 2. Configuración de Entorno
Debes crear un archivo `.env` en la raíz con las siguientes variables:
```env
# Conexión a Base de Datos (Neon)
DATABASE_URL=tu_url_de_neon_aqui

# Identidad Google Cloud
GOOGLE_PROJECT_ID=tu-id-de-proyecto
GOOGLE_LOCATION=us-central1
```

### 3. Inicialización de mi Memoria (SQL)
Para que pueda guardar traducciones en la caché, debes ejecutar este script SQL en tu base de datos:

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

---

## 📡 Cómo usar mi API

### `POST /translate`
Envía tus textos para ser localizados.

**Ejemplo de solicitud:**
```json
{
  "payload": {
    "WELCOME": "Welcome back, {{user}}!"
  },
  "target_lang": "Spanish",
  "tone": "Casual",
  "culture": "Peruvian"
}
```

**Mi respuesta:**
```json
{
  "translated_payload": {
    "WELCOME": "¡Qué bueno verte de nuevo, {{user}}!"
  },
  "from_cache": true
}
```

---

<div align="center">
  <p><b>Babel-Zilla Engine</b> - <i>"Traduciendo el futuro, una frase a la vez."</i></p>
</div>
