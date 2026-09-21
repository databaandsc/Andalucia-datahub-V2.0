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
        
    def load_facts(self):
        print("\n Iniciando carga de la tabla de hechos (registro_empleos)...")
        df = pl.read_parquet(self.parquet_path)
        
        # 1. Recuperamos los IDs reales generados por PostgreSQL
        query_sectores = "SELECT id AS id_sector, codigo_sector FROM sector"
        query_territorios = "SELECT id AS id_territorio, codigo_territorio FROM territorio"
        
        sectores_db = pl.read_database(query=query_sectores, connection=self.engine)
        territorios_db = pl.read_database(query=query_territorios, connection=self.engine)
        
        # 2. Cruzamos (JOIN) los datos del Parquet con los diccionarios
        df_hechos = df.join(sectores_db, on="codigo_sector", how="inner")
        df_hechos = df_hechos.join(territorios_db, on="codigo_territorio", how="inner")
        
        # 3. Preparar columnas: anio, trimestre, puestos
        
        df_final = df_hechos.with_columns([
            # Cortamos los primeros 4 caracteres para el año
            pl.col("codigo_periodo").str.slice(0, 4).cast(pl.Int32).alias("anio"),
            # Cortamos el último carácter para el trimestre
            pl.col("codigo_periodo").str.slice(4, 1).cast(pl.Int32).alias("trimestre"),
            # Convertimos el valor a número entero para los puestos
            pl.col("valor").cast(pl.Int32).alias("puestos")
        ])
        
        # Seleccionamos estrictamente lo que va a la base de datos
        df_final = df_final.select([
            "id_sector",
            "id_territorio",
            "anio",
            "trimestre",
            "puestos"
        ]).drop_nulls()
        
        print(f"Preparados {len(df_final)} registros listos para inyectar.")
        
        # 4. Inserción masiva en PostgreSQL
        with self.engine.begin() as connection:
            for row in df_final.iter_rows(named=True):
                query_insert = text("""
                    INSERT INTO registro_empleos (id_sector, id_territorio, anio, trimestre, puestos)
                    VALUES (:id_sec, :id_ter, :anio, :trim, :puestos)
                    ON CONFLICT DO NOTHING
                """)
                connection.execute(query_insert, {
                    "id_sec": row["id_sector"],
                    "id_ter": row["id_territorio"],
                    "anio": row["anio"],
                    "trim": row["trimestre"],
                    "puestos": row["puestos"]
                })
                
        print("Tabla de hechos cargada exitosamente.")

if __name__ == "__main__":
    loader = PostgresLoader()
    loader.inspect_data()
    loader.load_dimensions()
    loader.load_facts()