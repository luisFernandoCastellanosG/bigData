"""
Author: Luis Fernando Castellanos
Date: 2025-09-11
Description: este modulo son las funcion ayudantes para el proyecto de la clase de python
"""
import re
import os
import json
import requests
import sqlite3
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import io
import zipfile

class funciones:
    def __init__(self):
        print("Clase funciones iniciada para uso inmediato")

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
    
    """ Esta funcion revisa el contenido de una tabla en una base de datos SQLite y muestra un  numero limitado de registros."""
    def revisar_contenido_de_una_tabla(db_path, tabla_nombre, whereColumna='',whereValor='', limit=10, order_by_columna=None, order_asc=True):
        conn=sqlite3.connect(db_path)
        cursor=conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM "+tabla_nombre)
        total_registros=cursor.fetchone()[0]
        print(f"Total de registros en la tabla {tabla_nombre}: {total_registros}")
        sql="SELECT * FROM "+tabla_nombre
        params = ()
        if len(whereColumna)>0:
            sql+=" WHERE "+whereColumna+"=?"
            params = (whereValor,)
        if(order_by_columna):
            orderbyTipo="ASC" if order_asc else "DESC"
            sql+=f" ORDER BY {order_by_columna} {orderbyTipo}"
        sql+=" LIMIT "+str(limit)
        print(sql)
        cursor.execute(sql, params)
        resultados=cursor.fetchall()
        for fila in resultados:
            print(fila)
        conn.close()

    """ Esta funcion carga un archivo CSV en un DataFrame de pandas, asignando nombres de columnas especificados y manejando errores."""
    def cargar_data_desde_archivo_csv(ruta_archivo,columnas_nombre,pd):
        try:
            df_temporal = pd.read_csv(ruta_archivo,sep=';',header=None,encoding='latin-1',on_bad_lines='skip')
            #agregarle nombre de columnas al df creado
            df_temporal.columns=columnas_nombre
            if (len(df_temporal.columns)==len(columnas_nombre)):
                print(f" archivo {os.path.basename(ruta_archivo)} cargada exitosamente")
                return df_temporal
            else:
                print(f"archivo no trabajado {os.path.basename(ruta_archivo)} no tiene 10 columnas")
                return None

        except Exception as e:
            print(f"Error al procesar el archivo {os.path.basename(ruta_archivo)}: {str(e)}")
            return None
    
    def descomprimir_zip_local(self,ruta_file_zip, ruta_descomprimir):
      self.crear_carpeta(ruta_descomprimir)
      with zipfile.ZipFile(ruta_file_zip,'r') as zip_ref:
        total_files =len(zip_ref.namelist())
        with tqdm (total=total_files,desc='Descomprimiendo') as pbar:
          for member in zip_ref.infolist():
            zip_ref.extract(member,ruta_descomprimir)
            pbar.update(1)


    def descargar_y_descomprimir_zip(url, carpeta_destino, tipoArchivo=''):
        
        #os.makedirs(carpeta_destino, exist_ok=True)  #cree la carpeta sino existe
        self.crear_carpeta(carpeta_destino)
        response = requests.get(url)
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        if (tipoArchivo == ''):
            zip_file.extractall(carpeta_destino) #exportar .zip a la carpeta  
        else:
            for nombre_archivo in zip_file.namelist():
                if nombre_archivo.endswith(tipoArchivo):
                    zip_file.extract(nombre_archivo, carpeta_destino)