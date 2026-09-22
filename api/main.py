from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from api import models, schemas
from api.database import get_db

# 1. Instanciamos la aplicación principal. 
app = FastAPI(
    title="Andalucía DataHub API",
    description="Motor de consulta de empleos y sectores (v2.0)",
    version="2.0.0"
)

# 2. Creamos nuestro primer endpoint
@app.get("/")
def read_root():
    return {
        "estado": "Online",
        "mensaje": "Bienvenido a la API de Andalucía DataHub v2.0"
    }
    
# 3. Creamos un segundo endpoint para verificar el funcionamiento del sistema
@app.get("/api/v1/empleos", response_model=list[schemas.RegistroEmpleosResponse])
def obtener_empleos(db: Session = Depends(get_db), limite: int = 10):
    """
    Devuelve una lista de registros de empleo, limitados por defecto a 10 resultados
    para no sobrecargar la respuesta.
    """
    # 1. Hacemos la consulta a PostgreSQL usando el modelo
    empleos = db.query(models.RegistroEmpleo).limit(limite).all()
    
    # 2. Devolvemos los datos. FastAPI y Pydantic se encargan de transformarlos al JSON del schema
    return empleos