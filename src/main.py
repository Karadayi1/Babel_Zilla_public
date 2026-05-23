from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .database import test_connection
from .engine import get_ai_translation
from .crud import get_bulk_cached_translations, save_translation_to_db
from .schemas import TranslationRequest, TranslationResponse  # Importo los esquemas [cite: 1126]

app = FastAPI(title="Babel-Zilla API")

# Lista de dominios permitidos (mis frontends)
origins = [
    "http://localhost:4200", # Angular
    "http://localhost:4205", # Angular alternativo
    "http://localhost:3000", # React (estándar)
    "http://localhost:5433", # PostgreSQL
    "http://localhost:5173", # React (Vite)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permito cualquier origen para la extensión y fronts
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    test_connection()

@app.get("/")
def home():
    return {"message": "Babel-Zilla API is running. Check /docs for interactive testing."}

import time

@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    start_time = time.time()
    # Determino qué formato estoy procesando
    is_payload_mode = request.payload is not None
    input_texts = list(request.payload.values()) if is_payload_mode else (request.texts or [])
    keys = list(request.payload.keys()) if is_payload_mode else []

    if not input_texts:
        return TranslationResponse(translations=[], from_cache=True)

    final_translations = [None] * len(input_texts)
    texts_to_ai = []
    indices_to_ai = []

    # 1. Fase de Memoria: Búsqueda Masiva en Bloque
    cached_map = get_bulk_cached_translations(
        input_texts, 
        request.target_lang, 
        request.culture,
        request.tone, 
        request.context_hint
    )

    for i, text in enumerate(input_texts):
        if text in cached_map:
            final_translations[i] = cached_map[text]
        else:
            texts_to_ai.append(text)
            indices_to_ai.append(i)

    from_cache = len(texts_to_ai) == 0

    # 2. Fase de Cerebro: Batching con IA
    if texts_to_ai:
        ai_start = time.time()
        try:
            new_translations = get_ai_translation(
                text_batch=texts_to_ai, 
                target_lang=request.target_lang, 
                tone=request.tone, 
                culture=request.culture,
                context_hint=request.context_hint
            )
            print(f"Babel-Zilla: IA procesó {len(texts_to_ai)} textos en {time.time() - ai_start:.2f}s")

            for i, translation in enumerate(new_translations):
                original_index = indices_to_ai[i]
                final_translations[original_index] = translation
                save_translation_to_db(
                    texts_to_ai[i], translation, 
                    request.target_lang, request.tone, 
                    request.culture, request.context_hint
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en traducción: {str(e)}")

    total_time = (time.time() - start_time) * 1000
    source = "MEMORIA (PostgreSQL)" if from_cache else "CEREBRO (IA + DB)"
    print(f"Babel-Zilla: Petición resuelta por {source} en {total_time:.2f}ms")

    # 3. Preparo la respuesta según el formato original
    if is_payload_mode:
        translated_dict = {keys[i]: final_translations[i] for i in range(len(keys))}
        return TranslationResponse(translated_payload=translated_dict, from_cache=from_cache)
    else:
        return TranslationResponse(translations=final_translations, from_cache=from_cache)

@app.get("/test-brain")
def test_brain():
    """Mi prueba rápida original."""
    try:
        resultado = get_ai_translation(
            text_batch=["Hello World"], 
            target_lang="Spanish", 
            tone="Casual", 
            culture="Peruvian"
        )
        return {"status": "Mi Cerebro está activo", "resultado": resultado}
    except Exception as e:
        return {"status": "Mi Cerebro está desconectado", "error": str(e)}