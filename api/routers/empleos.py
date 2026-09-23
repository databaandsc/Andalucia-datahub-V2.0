from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from api import models, schemas
from api.database import get_db

router = APIRouter(
    prefix="/api/v1/empleos",
    tags=["Empleos"]
)

@router.get("/", response_model=list[schemas.RegistroEmpleosResponse])
def obtener_empleos(
    db: Session = Depends(get_db),
    limite: int = 100,
    anio: Optional[int] = None,
    trimestre: Optional[int] = None,
    puestos: Optional[int] = None,
    codigo_sector: Optional[str] = None,
    codigo_territorio: Optional[str] = None
):
    # 1. Iniciamos la consulta base a la tabla de hechos
    query = db.query(models.RegistroEmpleo)

    # 2. Vamos añadiendo filtros dinámicamente si el usuario los proporcionó
    if anio:
        query = query.filter(models.RegistroEmpleo.anio == anio)
        
    if trimestre:
        query = query.filter(models.RegistroEmpleo.trimestre == trimestre)
        pass
    
    if puestos:
        query = query.filter(models.RegistroEmpleo.puestos == puestos)
        pass
    
    if codigo_sector:
        query = query.join(models.Sector).filter(models.Sector.codigo_sector == codigo_sector)
        pass
    
    if codigo_territorio:
        query = query.join(models.Territorio).filter(models.Territorio.codigo_territorio == codigo_territorio)

    # 3. Finalmente, aplicamos el límite y ejecutamos la consulta
    empleos = query.limit(limite).all()
    
    return empleos