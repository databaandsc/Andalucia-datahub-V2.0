import os
from pathlib import Path
import polars as pl
from dotenv import load_dotenv
from sqlalchemy import create_engine

class PostgresLoader:
    def __init__(self):
        # 1. Configuración de rutas y variables
        self.root_dir = Path(__file__).parent.parent.parent
        load_dotenv(dotenv_path=self.root_dir / ".env")
        
        # 2. Conexión a Base de Datos
        self.engine = create_engine(os.getenv("DATABASE_URL"))
        
        # 3. Ruta al archivo Parquet (Ajusta el nombre de la carpeta si es necesario)
        # Aquí asumo que está en la raíz del proyecto
        self.parquet_path = self.root_dir / "data" / "cleaned_data.parquet"

    def inspect_data(self):
        """Lee el archivo Parquet y muestra su estructura para preparar el mapeo"""
        print(f"Buscando datos en: {self.parquet_path}")
        
        try:
            df = pl.read_parquet(self.parquet_path)
            print("¡Datos cargados en memoria con Polars!")
            
            print("\nEsquema del Parquet (Columnas):")
            print(df.schema)
            
            print("\nPrimeras 5 filas:")
            print(df.head(5))
            
        except FileNotFoundError:
            print(f"No se encuentra el archivo Parquet en la ruta: {self.parquet_path}")

if __name__ == "__main__":
    loader = PostgresLoader()
    loader.inspect_data()