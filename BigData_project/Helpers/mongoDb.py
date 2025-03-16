"""
Author      : Luis Fernando Castellanos Guarin
Date        : 2025-03-06
Description : son las clases para trabajar con MONGODB
"""
from pymongo import MongoClient

class MongoDb_functions:
    def consultar_documentos(coleccion, filtro=None):
        """imprimir listado de documentos"""
        try:
            if filtro:
                documents = coleccion.find(filtro)
            else:
                documents = coleccion.find()       
            for document in documents:
                print(document)   
        except Exception as e:
            print(f"Error al consultar documentos: {e}")

def consultar_total_documentos(coleccion):
    """imprimir total de documentos"""
    try:
        total_documents = coleccion.count_documents({})
        print(f"Total de documentos en la colección: {total_documents}")
    except Exception as e:
        print(f"Error al consultar total de documentos: {e}")

def crear_documento(coleccion, datos):
    """crear un documento"""
    try:
        result = coleccion.insert_one(datos)
        print(f"Documento creado con ID: {result.inserted_id}")
    except Exception as e:
        print(f"Error al crear documento: {e}")

def actualizar_documento(coleccion, filtro, nuevos_valores):
    """actualizar un documento"""
    try:
        result = coleccion.update_one(filtro, {"$set": nuevos_valores})
        if result.modified_count > 0:
            print("Documento actualizado")
        else:
            print("No se encontraron documentos para actualizar")
    except Exception as e:
        print(f"Error al actualizar documento: {e}")