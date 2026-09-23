from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api import models, schemas
from api.database import get_db

# 1. Instanciamos el router
router = APIRouter(
    prefix="/api/v1/territorios",
    tags=["Territorios"]
)

# 2. Endpoint para listar TODOS los territorios

@router.get("/", response_model=list[schemas.TerritorioResponse])
def obtener_territorios(db: Session = Depends(get_db)):
    """
    Devuelve una lista de todos los registros de territorios
    """
    # Hacemos la consulta a PostgreSQL
    territorios = db.query(models.Territorio).all()
    return territorios

# 3. Endpoint para buscar UN territorio por su código
@router.get("/{codigo}", response_model=schemas.TerritorioResponse)
def obtener_territorio_por_codigo(codigo: str, db: Session = Depends(get_db)):
    """
    Devuelve un registro de territorio filtrado por su codigo
    """
    territorio = db.query(models.Territorio).filter(models.Territorio.codigo_territorio == codigo).first()
    #Manejo de errores
    if not territorio:
        raise HTTPException(status_code=404, detail=f"El territorio con código '{codigo}' no existe.")
    
    return territorio   
    
    
    
    