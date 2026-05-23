import hashlib
from .database import get_db_connection, release_db_connection

def normalize_text(text: str):
    """Limpio el texto agresivamente para que la caché sea muy estable."""
    if not text: return ""
    # Elimino espacios extra, saltos de línea y normalizo puntuación común
    clean = " ".join(text.split()).strip().lower()
    # Normalizo comas decimales a puntos solo para el hash para evitar MISS por variaciones de la IA
    clean = clean.replace(",", ".")
    return clean

def generate_text_hash(text: str, lang: str, culture: str, tone: str, context_hint: str):
    # Uso el texto normalizado para el hash
    clean_text = normalize_text(text)
    # Añado culture a la llave para separar dialectos (MX vs ES, etc)
    key = f"{clean_text}|{lang}|{culture}|{tone}|{context_hint}".lower().strip()
    return hashlib.sha256(key.encode()).hexdigest()

def get_cached_translation(text: str, lang: str, culture: str, tone: str, context_hint: str):
    hash_id = generate_text_hash(text, lang, culture, tone, context_hint)

    conn = get_db_connection()
    if not conn: return None

    try:
        cur = conn.cursor()
        try:
            query = """
                SELECT t.texto_traducido 
                FROM traducciones t
                JOIN textos_originales o ON t.id_original = o.id
                JOIN perfiles_localizacion p ON t.id_perfil = p.id
                WHERE o.hash_id = %s AND p.idioma_destino = %s AND p.contexto_cultural = %s AND p.tono = %s
            """
            cur.execute(query, (hash_id, lang, culture, tone))
            result = cur.fetchone()
            if result:
                print(f"Babel-Zilla: HIT en caché para '{text[:20]}...' [Hash: {hash_id[:8]}]")
                return result[0]
            else:
                print(f"Babel-Zilla: MISS en caché para '{text[:20]}...' [Hash: {hash_id[:8]}]")
                return None
        finally:
            cur.close()
    except Exception as e:
        print(f"Error consultando caché: {e}")
        return None
    finally:
        release_db_connection(conn)

def get_bulk_cached_translations(texts: list, lang: str, culture: str, tone: str, context_hint: str):
    """Búsqueda masiva en caché para evitar el problema N+1."""
    if not texts:
        return {}

    # Genero el mapeo de hash -> texto_original
    hashes = []
    hash_to_text = {}
    for text in texts:
        h = generate_text_hash(text, lang, culture, tone, context_hint)
        hashes.append(h)
        hash_to_text[h] = text

    conn = get_db_connection()
    if not conn: return {}

    try:
        cur = conn.cursor()
        try:
            query = """
                SELECT o.hash_id, t.texto_traducido 
                FROM traducciones t
                JOIN textos_originales o ON t.id_original = o.id
                JOIN perfiles_localizacion p ON t.id_perfil = p.id
                WHERE o.hash_id IN %s AND p.idioma_destino = %s AND p.contexto_cultural = %s AND p.tono = %s
            """
            # psycopg2 maneja las tuplas para el IN automáticamente
            cur.execute(query, (tuple(hashes), lang, culture, tone))
            results = cur.fetchall()

            # Mapeo de vuelta: texto_original -> traduccion
            found = {hash_to_text[row[0]]: row[1] for row in results}
            print(f"Babel-Zilla: Búsqueda masiva completada. Encontrados {len(found)}/{len(texts)} en caché.")
            return found
        finally:
            cur.close()
    except Exception as e:
        print(f"Error en búsqueda masiva: {e}")
        return {}
    finally:
        release_db_connection(conn)

def save_translation_to_db(original: str, translated: str, lang: str, tone: str, culture: str, context_hint: str):
    # Mi hash debe ser consistente en el guardado también
    hash_id = generate_text_hash(original, lang, culture, tone, context_hint)
    conn = get_db_connection()
    if not conn: return

    try:
        cur = conn.cursor()
        try:
            # 1. Guardo el original (con su contexto en el hash)
            cur.execute("""
                INSERT INTO textos_originales (hash_id, contenido_original) 
                VALUES (%s, %s) 
                ON CONFLICT (hash_id) DO NOTHING 
                RETURNING id
            """, (hash_id, original))

            row = cur.fetchone()
            if row:
                original_id = row[0]
            else:
                # Si ya existía, lo busco para obtener el ID
                cur.execute("SELECT id FROM textos_originales WHERE hash_id = %s", (hash_id,))
                original_id = cur.fetchone()[0]

            # 2. Busco el ID del perfil que coincida con el idioma y tono
            cur.execute("""
                SELECT id FROM perfiles_localizacion 
                WHERE idioma_destino = %s AND tono = %s AND contexto_cultural = %s
            """, (lang, tone, culture))

            perfil = cur.fetchone()
            if perfil:
                perfil_id = perfil[0]
            else:
                # Si no existe el perfil, lo creo para no romper la relación
                cur.execute("""
                    INSERT INTO perfiles_localizacion (idioma_destino, tono, contexto_cultural)
                    VALUES (%s, %s, %s) RETURNING id
                """, (lang, tone, culture))
                perfil_id = cur.fetchone()[0]

            # 3. Guardo la traducción final
            cur.execute("""
                INSERT INTO traducciones (id_original, id_perfil, texto_traducido) 
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (original_id, perfil_id, translated))

            conn.commit()
        finally:
            cur.close()
    except Exception as e:
        print(f"Error al intentar guardar en mi DB: {e}")
        try:
            conn.rollback()
        except:
            pass # Si el rollback falla, ya perdimos la conexión
    finally:
        release_db_connection(conn)