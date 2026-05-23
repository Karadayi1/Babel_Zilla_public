from pydantic import BaseModel
from typing import List, Optional, Dict

# Lo que recibo de mi Frontend (Angular/React)
class TranslationRequest(BaseModel):
    # Puedo recibir una lista simple o un diccionario estructurado
    texts: Optional[List[str]] = None
    payload: Optional[Dict[str, str]] = None  # Ejemplo: {"WELCOME_MSG": "Hola {{user}}"}

    target_lang: str
    tone: str
    culture: str
    context_hint: Optional[str] = "General web interface"

# Lo que mi Babel-Zilla responde
class TranslationResponse(BaseModel):
    # Devuelvo el mismo formato que recibí
    translations: Optional[List[str]] = None
    translated_payload: Optional[Dict[str, str]] = None

    from_cache: bool