from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api import models, schemas
from api.database import get_db

# 1. Instanciamos el router
router = APIRouter(
    prefix="/api/v1/sectores",
    tags=["Sectores"] # Organiza el Swagger
)


# 2. Endpoint para listar TODOS los sectores

@router.get("/", response_model=list[schemas.SectorResponse])
def obtener_sectores(db: Session = Depends(get_db)):
    """
    Devuelve una lista de todos los registros de sectores
    """
    # Hacemos la consulta a PostgreSQL
    sectores = db.query(models.Sector).all()
    return sectores

# 3. Endpoint para buscar UN sector por su código

@router.get("/{codigo}", response_model=list[schemas.SectorResponse])
def obtener_sector_por_codigo(codigo: str, db: Session = Depends(get_db)):
    """"
    Devuelve un registro de sector filtrado por su codigo
    """
    sector = db.query(models.Sector).filter(models.Sector.codigo_sector == codigo).first()
    # Manejo de errores: Si el sector no existe en la base de datos, lanzamos un 404
    if not sector:
        raise HTTPException(status_code=404, detail=f"El sector con código '{codigo}' no existe.")
        
    return sector
    
    