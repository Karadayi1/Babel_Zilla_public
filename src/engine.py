from google import genai
import re
from .config import settings

# Inicializo el cliente para Vertex AI
client = genai.Client(
    vertexai=True, 
    project=settings.GOOGLE_PROJECT_ID,
    location=settings.GOOGLE_LOCATION
)

def get_ai_translation(text_batch: list, target_lang: str, tone: str, culture: str, context_hint: str = "General web interface"):
    # Usamos Gemini 2.5 Flash (el motor más avanzado y rápido)
    model_id = "gemini-2.5-flash" 
    
    # MODIFICACIÓN V2.1: Enfoque de Lingüista Dinámico Universal
    sys_instruct = f"""
    Eres el Motor de Localización Babel-Zilla v2.1.
    Actúa como un filólogo y hablante nativo experto de la región específica: "{culture}".
    Tu objetivo es traducir textos al idioma {target_lang} respetando la cultura {culture} y un tono {tone}.

    REGLAS GRAMATICALES DINÁMICAS:
    1. Adapta la gramática (voseo, tuteo o ustedeo) de forma natural según las convenciones predominantes de "{culture}" para el tono "{tone}".
    2. Usa el vocabulario técnico y cotidiano específico de esa región (ej. Coche vs Auto vs Carro).

    REGLAS CRÍTICAS DE PRESERVACIÓN:
    1. VARIABLES: No traduzcas ni alteres NUNCA lo que esté dentro de llaves dobles {{{{...}}}} o llaves simples {{...}}.
    2. MARCAS: No traduzcas nombres propios de tecnología o marcas (Babel-Zilla, Vertex AI, Google, etc.).
    3. CÓDIGO/HTML: Mantén las etiquetas HTML en sus posiciones relativas correctas.
    
    REGLA DE FORMATO ESTRICTA:
    - Las traducciones deben ser texto puro.
    - Tienes PROHIBIDO incluir prefijos de lista, viñetas o números al inicio de tus respuestas.
    """

    # Preparo mis textos como una lista numerada para que la IA no pierda el orden
    formatted_list = "\n".join([f"{i+1}. {text}" for i, text in enumerate(text_batch)])

    prompt = f"""
    CONTEXTO DE LA APP: {context_hint}
    IDIOMA DESTINO: {target_lang}

    TAREA:
    Traduce los siguientes textos siguiendo las REGLAS DINÁMICAS. 
    Responde ÚNICAMENTE con las traducciones, una por cada línea, sin repetir el número.
    Usa el separador '|||' al final de cada traducción para garantizar la segmentación.

    TEXTOS A TRADUCIR:
    {formatted_list}
    """

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config={'system_instruction': sys_instruct}
        )
        
        # Proceso y limpio: elimino espacios vacíos y el separador
        raw_results = response.text.strip().split("|||")
        
        # Limpieza Regex: Elimina números de lista si la IA alucina (ej: "1. ", "2. ")
        translations = [re.sub(r'^\d+\.\s*', '', t.strip()) for t in raw_results if t.strip()]

        # Validación de seguridad: si mi IA se salta alguna línea, lanzo una alerta
        if len(translations) != len(text_batch):
            print(f"Warning: Se enviaron {len(text_batch)} textos pero se recibieron {len(translations)}")

        return translations

    except Exception as e:
        print(f"Error en la comunicación con el modelo: {e}")
        raise e
