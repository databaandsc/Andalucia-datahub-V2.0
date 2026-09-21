from fastapi import FastAPI

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