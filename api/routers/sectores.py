from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api import models, schemas
from api.database import get_db

# Instanciamos el router
router = APIRouter(
    prefix="/api/v1/sectores",
    tags=["Sectores"] # Organiza el Swagger
)

# 3. Creamos un segundo endpoint para verificar el funcionamiento del sistema
@router.get("/", response_model=list[schemas.SectorResponse])
def obtener_sectores(db: Session = Depends(get_db), limite: int = 10):
    """
    Devuelve una lista de registros de sectores, limitados por defecto a 10 resultados
    para no sobrecargar la respuesta.
    """
    # 1. Hacemos la consulta a PostgreSQL usando el modelo
    sectores = db.query(models.Sector).limit(limite).all()
    
    # 2. Devolvemos los datos. FastAPI y Pydantic se encargan de transformarlos al JSON del schema
    return sectores