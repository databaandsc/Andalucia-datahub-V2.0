from pydantic import BaseModel

# --- ESQUEMAS DE DIMENSIONES ---

class SectorResponse(BaseModel):
    id: int
    codigo_sector: str
    descripcion_sector: str | None = None
    
    class Config:
        from_attributes = True
        
class TerritorioResponse(BaseModel):
    id: int
    codigo_territorio: str
    descripcion_territorio: str | None = None
    
    class Config:
        from_attributes = True

# --- ESQUEMA DE HECHOS ---

class RegistroEmpleosResponse(BaseModel):
    id: int
    anio: int
    trimestre: int
    puestos: int
    
    sector: SectorResponse
    territorio: TerritorioResponse

    class Config:
        from_attributes = True