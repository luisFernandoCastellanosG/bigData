"""
Author: Luis Fernando Castellanos
Date: 2025-09-11
Description: este modulo son las funciones sobre mongoDB
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime
class mongoDB_operaciones:
    def __init__(self, uri, db_name):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None

    def conectar(self):
        try:
            self.client = MongoClient(self.uri)
            # Verificar la conexión
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            print(f"Conectado a la base de datos MongoDB: {self.db_name}")
        except ConnectionFailure as e:
            print(f"Error de conexión a MongoDB: {str(e)}")
            self.client = None
            self.db = None

    def insertar_documento(self, coleccion_nombre, documento):
        if self.db:
            coleccion = self.db[coleccion_nombre]
            resultado = coleccion.insert_one(documento)
            print(f"Documento insertado con ID: {resultado.inserted_id}")
        else:
            print("No hay conexión a la base de datos.")

    def buscar_documentos(self, coleccion_nombre, filtro={}, limite=10):
        if self.db:
            coleccion = self.db[coleccion_nombre]
            resultados = coleccion.find(filtro).limit(limite)
            for doc in resultados:
                print(doc)
        else:
            print("No hay conexión a la base de datos.")

    def consultar_total_documentos(self, coleccion_nombre):
        if self.db:
            coleccion = self.db[coleccion_nombre]
            total = coleccion.count_documents({})
            print(f"Total de documentos en la colección {coleccion_nombre}: {total}")
            return total
        else:
            print("No hay conexión a la base de datos.")
            return 0
        
    def actualizar_documento(self, coleccion_nombre, filtro, actualizacion):
        if self.db:
            coleccion = self.db[coleccion_nombre]
            resultado = coleccion.update_one(filtro, {'$set': actualizacion})
            print(f"Documentos modificados: {resultado.modified_count}")
        else:
            print("No hay conexión a la base de datos.")

    def actualizar_varios_documentos(self, coleccion_nombre, filtro, actualizacion):
        if self.db:
            coleccion = self.db[coleccion_nombre]
            resultado = coleccion.update_many(filtro, {'$set': actualizacion})
            print(f"Documentos modificados: {resultado.modified_count}")
        else:
            print("No hay conexión a la base de datos.")

    def eliminar_documento(self, coleccion_nombre, filtro):
        if self.db:
            coleccion = self.db[coleccion_nombre]
            resultado = coleccion.delete_one(filtro)
            print(f"Documentos eliminados: {resultado.deleted_count}")
        else:
            print("No hay conexión a la base de datos.")

    def eliminar_varios_documentos(self, coleccion_nombre, filtro):
        if self.db:
            coleccion = self.db[coleccion_nombre]
            resultado = coleccion.delete_many(filtro)
            print(f"Documentos eliminados: {resultado.deleted_count}")
        else:
            print("No hay conexión a la base de datos.")

    def cerrar_conexion(self):
        if self.client:
            self.client.close()
            print("Conexión a MongoDB cerrada.")