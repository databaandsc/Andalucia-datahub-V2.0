from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Sector(Base):
    __tablename__ = "sector"
    
    # Clave primaria
    id = Column(Integer, primary_key=True, index=True)
    
    # Resto de columnas
    codigo_sector = Column(String, unique=True, nullable=False)
    descripcion_sector = Column(String, nullable=False)
    
class Territorio(Base):
    __tablename__ = "territorio"
    
    # Clave primaria
    id = Column(Integer, primary_key=True, index=True)
    
    # Resto de columnas
    codigo_territorio = Column(String, unique=True, nullable=False)
    descripcion_territorio = Column(String, nullable=False)

class RegistroEmpleo(Base):
    __tablename__ = "registro_empleos"
    
    # Clave primaria
    id = Column(Integer, primary_key=True, index=True)
    
    #Claves foraneas
    id_sector = Column(Integer, ForeignKey("sector.id"), nullable=False)    
    id_territorio = Column(Integer, ForeignKey("territorio.id"), nullable=False)
    
    # Resto de columnas
    anio = Column(Integer, nullable=False)
    trimestre = Column(Integer, nullable=False)
    puestos = Column(Integer, nullable=False)
    
    # Relaciones (ORM)
    sector = relationship("Sector")
    territorio = relationship("Territorio")
    
    