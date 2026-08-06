import requests
import json
from pathlib import Path

def download_ieca_data(url: str, output_filename: str = "raw_data.json") -> Path:
    """
    Descarga el JSON de la API del IECA y lo guarda localmente.
    Si el archivo ya existe, se omite la descarga para no saturar la API.
    """
    print(f"Iniciando proceso para: {url}")
    
    # Apuntamos a la carpeta 'data' en la raíz del proyecto
    # Path(__file__).parent sube niveles hasta llegar a la raíz
    root_dir = Path(__file__).parent.parent.parent
    data_dir = root_dir / "data"
    
    # Aseguramos que la carpeta exista por si acaso
    data_dir.mkdir(exist_ok=True)
    
    file_path = data_dir / output_filename

    # Lógica de caché local: si ya lo tenemos, no lo volvemos a bajar
    if file_path.exists():
        print(f"El archivo {output_filename} ya existe en local.")
        return file_path

    print("Descargando datos desde la API (esto puede tardar unos segundos)...")
    try:
        # Hacemos la petición GET
        response = requests.get(url, timeout=60)
        
        # Si el servidor devuelve un error, lanzamos una excepción
        response.raise_for_status() 
        
        # Guardamos el JSON crudo en disco
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=2)
            
        print(f"Descarga completada con éxito. Guardado en: {file_path}")
        return file_path
        
    except requests.exceptions.RequestException as e:
        print(f" Error al descargar los datos: {e}")
        raise

if __name__ == "__main__":
    URL_IECA = "https://www.juntadeandalucia.es/institutodeestadisticaycartografia/intranet/admin/rest/v1.0/consulta/106159" 
    
    download_ieca_data(URL_IECA)