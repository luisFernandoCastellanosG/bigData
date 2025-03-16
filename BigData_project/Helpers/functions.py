"""
Author      : Luis Fernando Castellanos Guarin
Date        : 2025-03-06
Description : son las clases para trabajar funciones generales (array, carpetas, archivos, texto, etc)
"""
import re
import os
import io
import unicodedata
import requests
import zipfile
from pathlib import Path
class functions:
  def __init__(self):
    print('<<---Inializando class functions-->>')
         
  def crear_carpeta(self,ruta):
    """crear carpeta"""
    try:
        if not os.path.exists(ruta):
            os.makedirs(ruta)
            print(f"Carpeta creada: {ruta}")
        else:
            print(f"La carpeta ya existe: {ruta}")
    except Exception as e:
        print(f"Error al crear carpeta: {e}")
  
  def descargar_y_descomprimir_zip(self,url, destino,todo=True):
    #definiendo la URL donde esta el ZIP
    #crear directorio en caso de no existir
    os.makedirs(destino, exist_ok=True)
    response = requests.get(url)
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    if todo==True:
      zip_file.extractall(destino)   #extraer todo sin importar
    else:
      #----extraer los archivo por extensión---
      for file_name in zip_file.namelist():
        if file_name.endswith(('.csv','.txt')):     #extraer unicamente los CSV y txt
          zip_file.extract(file_name, path=destino)
