import json
from pathlib import Path
import polars as pl

def explore_ieca_data(input_filename: str = "raw_data.json"):
    """
    Lee el archivo JSON local crudo y lo carga en un DataFrame de Polars
    para extraer tanto los códigos oficiales como las descripciones.
    """
    # 1. Localizar el archivo en nuestra carpeta 'data'
    root_dir = Path(__file__).parent.parent.parent
    file_path = root_dir / "data" / input_filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"No se encuentra el archivo {file_path}. Ejecuta el extractor primero.")

    print(f"Leyendo el archivo local: {input_filename}...")
    
    # 2. Cargar el JSON 
    with open(file_path, "r", encoding="utf-8") as f:
        raw_json = json.load(f)
        
    datos_crudos = raw_json.get("data", [])
    
    if not datos_crudos:
         print("No se encontró la clave 'data' o el array está vacío.")
         return None

    print(f"Procesando {len(datos_crudos)} filas...")
    
    # 3. Creación del DataFrame base
    df = pl.DataFrame(datos_crudos, orient="row")
    
    # Bautizamos las columnas originales temporalmente
    df = df.rename({
        "column_0": "sector_raw",
        "column_1": "periodo_raw",
        "column_2": "territorio_raw",
        "column_3": "tipo_dato_raw",
        "column_4": "valor_raw"
    })
    
    # Aplanamos los structs para extraer códigos y descripciones oficiales
    df = df.with_columns([
        # SECTOR: Código y descripción
        pl.col("sector_raw").struct.field("cod").list.get(0).alias("codigo_sector"),
        pl.col("sector_raw").struct.field("des").alias("sector"),
        
        # PERIODO: Código y descripción
        pl.col("periodo_raw").struct.field("cod").list.get(0).alias("codigo_periodo"),
        pl.col("periodo_raw").struct.field("des").alias("periodo"),
        
        # TERRITORIO: Código y descripción
        pl.col("territorio_raw").struct.field("cod").list.get(0).alias("codigo_territorio"),
        pl.col("territorio_raw").struct.field("des").alias("territorio"),
        
        # TIPO DE DATO
        pl.col("tipo_dato_raw").struct.field("des").alias("tipo_dato"),
        
        # VALOR: Extraído y convertido a Float64
        pl.col("valor_raw").struct.field("val").cast(pl.Float64).alias("valor")
    ])

    # Seleccionamos estrictamente el orden y las columnas limpias finales
    df = df.select([
        "codigo_sector", "sector",
        "codigo_territorio", "territorio",
        "codigo_periodo", "periodo",
        "tipo_dato", "valor"
    ])

    # 4. Imprimimos un vistazo rápido para verificar
    print("\n=== VISTAZO AL DATAFRAME LIMPIO ===")
    print(df.head(5))  
    
    print("\n=== ESQUEMA FINAL DEL DATAFRAME ===")
    print(df.schema)
    
    # 5. Definimos la ruta de salida en la carpeta data
    output_path = root_dir / "data" / "cleaned_data.parquet"
    
    # 6. Guardamos el nuevo Parquet enriquecido
    df.write_parquet(output_path)
    print(f"Datos limpios con códigos guardados exitosamente en: {output_path}")

    return df

if __name__ == "__main__":
    explore_ieca_data()