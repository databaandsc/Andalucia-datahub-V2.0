import polars as pl
import json
from pathlib import Path

def explore_ieca_data(input_filename: str = "raw_data.json"):
    """
    Lee el archivo JSON local crudo y lo carga en un DataFrame de Polars
    para comenzar la exploración y limpieza.
    """
    # 1. Localizar el archivo en nuestra carpeta 'data'
    root_dir = Path(__file__).parent.parent.parent
    file_path = root_dir / "data" / input_filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"No se encuentra el archivo {file_path}. Ejecuta el extractor primero.")

    print(f"Leyendo el archivo local: {input_filename}...")
    
    # 2. Cargar el JSON con la librería estándar de Python
    with open(file_path, "r", encoding="utf-8") as f:
        raw_json = json.load(f)
        
    datos_crudos = raw_json.get("data", [])
    
    if not datos_crudos:
         print("No se encontró la clave 'data' o el array está vacío.")
         return None

    print(f"Inyectando {len(datos_crudos)} filas")
    
 # 3. Creación del DataFrame
    # orient="row" fuerza a que cada lista interna del JSON sea una nueva fila (observación)
    df = pl.DataFrame(datos_crudos, orient="row")
    
    # Bautizamos las columnas usando el conocimiento de negocio que ya tienes
    df = df.rename({
        "column_0": "sector",
        "column_1": "periodo",
        "column_2": "territorio",
        "column_3": "tipo_dato",
        "column_4": "valor"
    })
    
    # 4. Aplanamos los structs para que cada campo sea una columna separada
    df = df.with_columns([
        # Entramos al struct y sacamos el campo 'des' (Descripción)
        pl.col("sector").struct.field("des").alias("sector"),
        pl.col("periodo").struct.field("des").alias("periodo"),
        pl.col("territorio").struct.field("des").alias("territorio"),
        pl.col("tipo_dato").struct.field("des").alias("tipo_dato"),
        
        # En el valor sacamos 'val' y lo forzamos a ser un número decimal (Float64)
        pl.col("valor").struct.field("val").cast(pl.Float64).alias("valor")
    ])

    # 4. Imprimimos un vistazo rápido al DataFrame
    print("\n=== VISTAZO AL DATAFRAME CRUDO ===")
    print(df.head(5))  
    
    print("\n=== TIPOS DE DATOS INICIALES ===")
    print(df.schema)

    return df

if __name__ == "__main__":
    explore_ieca_data()