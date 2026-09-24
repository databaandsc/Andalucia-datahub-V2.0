import os
import json
import requests
from pathlib import Path
import polars as pl
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

class AndaluciaETL:
    def __init__(self):
        # 1. Definir rutas relativas
        self.root_dir = Path(__file__).parent.parent
        self.data_dir = self.root_dir / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.raw_json_path = self.data_dir / "raw_data.json"
        self.parquet_path = self.data_dir / "cleaned_data.parquet"
        
        # 2. Configurar base de datos (Prioriza variable inyectada, luego lee .env local)
        load_dotenv(dotenv_path=self.root_dir / ".env")
        
        database_url = os.getenv("DATABASE_URL")
        
        # Si la URL viene de Docker, hay que cambiarla de postgresql:// a postgresql+psycopg2:// para SQLAlchemy
        if database_url and database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
            
        if not database_url:
            user = os.getenv("DB_USER", "postgres")
            password = os.getenv("DB_PASSWORD", "postgres")
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", "5432")
            db_name = os.getenv("DB_NAME", "andalucia_datahub")
            database_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"

        print(f"Conectando a BD usando host: {database_url.split('@')[1].split(':')[0]}")
        self.engine = create_engine(database_url)

    def extract_from_api(self, url: str):
        """Descarga el JSON de la API del IECA."""
        if self.raw_json_path.exists():
            print(f"1. EXTRACCIÓN: El archivo {self.raw_json_path.name} ya existe. Omitiendo descarga.")
            return

        print(f"1. EXTRACCIÓN: Descargando datos desde IECA...")
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status() 
            with open(self.raw_json_path, "w", encoding="utf-8") as f:
                json.dump(response.json(), f, ensure_ascii=False, indent=2)
            print("Extracción completada.")
        except Exception as e:
            print(f"Error en extracción: {e}")
            raise

    def transform_to_parquet(self):
        """Limpia el JSON con Polars y guarda en Parquet."""
        print("2. TRANSFORMACIÓN: Procesando JSON con Polars...")
        if not self.raw_json_path.exists():
            raise FileNotFoundError("No hay datos crudos para transformar.")

        with open(self.raw_json_path, "r", encoding="utf-8") as f:
            raw_json = json.load(f)
            
        datos_crudos = raw_json.get("data", [])
        df = pl.DataFrame(datos_crudos, orient="row")
        
        df = df.rename({
            "column_0": "sector_raw", "column_1": "periodo_raw",
            "column_2": "territorio_raw", "column_3": "tipo_dato_raw",
            "column_4": "valor_raw"
        })
        
        df = df.with_columns([
            pl.col("sector_raw").struct.field("cod").list.get(0).alias("codigo_sector"),
            pl.col("sector_raw").struct.field("des").alias("sector"),
            pl.col("periodo_raw").struct.field("cod").list.get(0).alias("codigo_periodo"),
            pl.col("periodo_raw").struct.field("des").alias("periodo"),
            pl.col("territorio_raw").struct.field("cod").list.get(0).alias("codigo_territorio"),
            pl.col("territorio_raw").struct.field("des").alias("territorio"),
            pl.col("tipo_dato_raw").struct.field("des").alias("tipo_dato"),
            pl.col("valor_raw").struct.field("val").cast(pl.Float64).alias("valor")
        ])

        df = df.select([
            "codigo_sector", "sector", "codigo_territorio", "territorio",
            "codigo_periodo", "periodo", "tipo_dato", "valor"
        ])
        
        df.write_parquet(self.parquet_path)
        print("Transformación completada. Guardado como Parquet.")

    def load_to_database(self):
        """Carga dimensiones y hechos a PostgreSQL."""
        print("3. CARGA: Inyectando datos en PostgreSQL...")
        df = pl.read_parquet(self.parquet_path)
        
        sectores_df = df.select(["codigo_sector", "sector"]).unique()
        territorios_df = df.select(["codigo_territorio", "territorio"]).unique()
        
        with self.engine.begin() as connection:
            # Dimensiones
            print(" -> Cargando Sectores...")
            for row in sectores_df.iter_rows(named=True):
                connection.execute(text(
                    "INSERT INTO sector (codigo_sector, descripcion_sector) VALUES (:c, :d) ON CONFLICT DO NOTHING"
                ), {"c": row["codigo_sector"], "d": row["sector"]})
                
            print(" -> Cargando Territorios...")
            for row in territorios_df.iter_rows(named=True):
                connection.execute(text(
                    "INSERT INTO territorio (codigo_territorio, descripcion_territorio) VALUES (:c, :d) ON CONFLICT DO NOTHING"
                ), {"c": row["codigo_territorio"], "d": row["territorio"]})
                
        # Hechos
        query_sectores = "SELECT id AS id_sector, codigo_sector FROM sector"
        query_territorios = "SELECT id AS id_territorio, codigo_territorio FROM territorio"
        
        sectores_db = pl.read_database(query=query_sectores, connection=self.engine)
        territorios_db = pl.read_database(query=query_territorios, connection=self.engine)
        
        df_hechos = df.join(sectores_db, on="codigo_sector", how="inner")
        df_hechos = df_hechos.join(territorios_db, on="codigo_territorio", how="inner")
        
        df_final = df_hechos.with_columns([
            pl.col("codigo_periodo").str.slice(0, 4).cast(pl.Int32).alias("anio"),
            pl.col("codigo_periodo").str.slice(4, 1).cast(pl.Int32).alias("trimestre"),
            pl.col("valor").cast(pl.Int32).alias("puestos")
        ]).select(["id_sector", "id_territorio", "anio", "trimestre", "puestos"]).drop_nulls()
        
        print(" -> Cargando Tabla de Hechos (Registro de Empleos)...")
        with self.engine.begin() as connection:
            for row in df_final.iter_rows(named=True):
                connection.execute(text(
                    "INSERT INTO registro_empleos (id_sector, id_territorio, anio, trimestre, puestos) VALUES (:s, :t, :a, :tr, :p) ON CONFLICT DO NOTHING"
                ), {"s": row["id_sector"], "t": row["id_territorio"], "a": row["anio"], "tr": row["trimestre"], "p": row["puestos"]})
                
        print("Carga completada con éxito. ¡Base de datos llena!")

if __name__ == "__main__":
    URL_IECA = "https://www.juntadeandalucia.es/institutodeestadisticaycartografia/intranet/admin/rest/v1.0/consulta/106159"
    
    etl = AndaluciaETL()
    etl.extract_from_api(URL_IECA)
    etl.transform_to_parquet()
    etl.load_to_database()