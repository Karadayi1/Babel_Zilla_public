import psycopg2
from psycopg2 import pool
from .config import settings

# Inicializo el pool de conexiones (Mínimo 1, Máximo 20 para Babel-Zilla)
db_pool = None

def init_db_pool():
    global db_pool
    if not db_pool:
        try:
            db_pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=20,
                dsn=settings.DATABASE_URL
            )
            print("Babel-Zilla: Pool de conexiones PostgreSQL inicializado.")
        except Exception as e:
            print(f"Error inicializando el pool: {e}")

def get_db_connection():
    if not db_pool:
        init_db_pool()
    return db_pool.getconn()

def release_db_connection(conn):
    if db_pool and conn:
        db_pool.putconn(conn)

def test_connection():
    try:
        conn = get_db_connection()
        if conn:
            print("Conexión exitosa: Mi Memoria de Babel-Zilla (PostgreSQL) está lista.")
            release_db_connection(conn)
    except Exception as e:
        print(f"Alerta: Mi motor de base de datos no responde: {e}")