"""
Author      : Luis Fernando Castellanos Guarin
Date        : 2025-03-06
Description : son las clases para trabajar con MONGODB
"""
from pymongo import MongoClient
import json
class MongoDb_functions:
  def __init__(self):
    print('<<---Inializando class funciones CRUD de mongoDB-->>')
    
  def consultar_documentos(self, coleccion, filtro=None,cant_documentos=50):
    """imprimir listado de documentos"""
    print("se visualizaran solo ",cant_documentos, ' registros')
    try:
        if filtro:
            documents = coleccion.find(filtro).limit(cant_documentos)
        else:
            documents = coleccion.find().limit(cant_documentos)       
        for document in documents:
            print(json.dumps(document, indent=4))  
    except Exception as e:
        print(f"Error al consultar documentos: {e}")

  def consultar_total_documentos(self,coleccion):
    """imprimir total de documentos"""
    try:
        total_documents = coleccion.count_documents({})
        print(f"Total de documentos en la colección: {total_documents}")
    except Exception as e:
        print(f"Error al consultar total de documentos: {e}")

  def crear_documento(self,coleccion, datos):
    """crear un documento"""
    try:
        result = coleccion.insert_one(datos)
        print(f"Documento creado con ID: {result.inserted_id}")
    except Exception as e:
        print(f"Error al crear documento: {e}")

  def actualizar_documento(self,coleccion, filtro, nuevos_valores):
    """actualizar un documento"""
    try:
        result = coleccion.update_one(filtro, {"$set": nuevos_valores})
        if result.modified_count > 0:
            print("Documento actualizado")
        else:
            print("No se encontraron documentos para actualizar")
    except Exception as e:
        print(f"Error al actualizar documento: {e}")