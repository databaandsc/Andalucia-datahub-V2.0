from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from api import models, schemas
from api.database import get_db
from api.routers import sectores, territorios

# 1. Instanciamos la aplicación principal. 
app = FastAPI(
    title="Andalucía DataHub API",
    description="Motor de consulta de empleos y sectores (v2.0)",
    version="2.0.0"
)

# Le decimos a la app principal que enchufe el bloque de rutas de sectores
app.include_router(sectores.router)
app.include_router(territorios.router)

@app.get("/")
def read_root():
    return {"estado": "Online"}