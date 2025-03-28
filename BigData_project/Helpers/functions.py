"""
Author      : Luis Fernando Castellanos Guarin
Date        : 2025-03-06
Description : son las clases para trabajar funciones generales (array, carpetas, archivos, texto, etc)
"""
import re
import os
import io
import json
import unicodedata
import requests
import zipfile
from pathlib import Path
from tqdm import tqdm
class functions:
  def __init__(self):
    print('<<---Inializando funciones generales-->>')
         
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

  def descomprimir_zip_local(self,zip_file_url, destino):
    #definiendo la ruta local donde esta el ZIP
    #crear directorio en caso de no existir
    os.makedirs(destino, exist_ok=True)
    with zipfile.ZipFile(zip_file_url, 'r') as zip_ref:
      total_files = len(zip_ref.namelist())
      with tqdm(total=total_files, desc="Descomprimiendo archivos") as pbar:
          for member in zip_ref.infolist():
              zip_ref.extract(member, destino)
              pbar.update(1)
