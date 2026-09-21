import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Recuperamos las credenciales del archivo .env
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "andalucia_datahub")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Motor de conexión
engine = create_engine(DATABASE_URL)

# Creador de sesiones: cada petición HTTP abrirá y cerrará su propia sesión limpia
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependencia para inyectar la sesión en los endpoints de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        # --- Bloque de prueba temporal ---
if __name__ == "__main__":
    try:
        # Intentamos abrir una conexión directa con el motor
        with engine.connect() as connection:
            print("¡Conexión exitosa a PostgreSQL desde la API!")
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")