import os
from pathlib import Path
import polars as pl
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

class PostgresLoader:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent.parent
        load_dotenv(dotenv_path=self.root_dir / ".env")
        
        self.engine = create_engine(os.getenv("DATABASE_URL"))
        self.parquet_path = self.root_dir / "data" / "cleaned_data.parquet"

    def inspect_data(self):
        print(f"Buscando datos en: {self.parquet_path}")
        try:
            df = pl.read_parquet(self.parquet_path)
            print("Datos cargados en memoria con Polars")
            print(f"Total de filas en el Parquet: {len(df)}")
        except FileNotFoundError:
            print(f"No encuentro el archivo Parquet en la ruta: {self.parquet_path}")

    def load_dimensions(self):
        """Extrae códigos y descripciones únicas de sectores y territorios y los inserta en PostgreSQL"""
        print("\nIniciando carga de dimensiones...")
        df = pl.read_parquet(self.parquet_path)
        
        # 1. Extraer combinaciones únicas de sectores
        sectores_df = df.select(["codigo_sector", "sector"]).unique()
        
        # 2. Extraer combinaciones únicas de territorios
        territorios_df = df.select(["codigo_territorio", "territorio"]).unique()
        
        print(f"Encontrados {len(sectores_df)} sectores únicos y {len(territorios_df)} territorios únicos.")
        
        # 3. Inyectar en PostgreSQL apuntando al conflicto por el 'codigo'
        with self.engine.begin() as connection:
            
            # Insertar Sectores (Controlando conflicto en codigo_sector)
            for row in sectores_df.iter_rows(named=True):
                query_sector = text("""
                    INSERT INTO sector (codigo_sector, descripcion_sector) 
                    VALUES (:codigo, :desc) 
                    ON CONFLICT (codigo_sector) DO NOTHING
                """)
                connection.execute(query_sector, {
                    "codigo": row["codigo_sector"], 
                    "desc": row["sector"]
                })
                
            # Insertar Territorios (Controlando conflicto en codigo_territorio)
            for row in territorios_df.iter_rows(named=True):
                query_territorio = text("""
                    INSERT INTO territorio (codigo_territorio, descripcion_territorio) 
                    VALUES (:codigo, :desc) 
                    ON CONFLICT (codigo_territorio) DO NOTHING
                """)
                connection.execute(query_territorio, {
                    "codigo": row["codigo_territorio"], 
                    "desc": row["territorio"]
                })
                
        print("Dimensiones cargadas correctamente en PostgreSQL")

if __name__ == "__main__":
    loader = PostgresLoader()
    loader.inspect_data()
    loader.load_dimensions()