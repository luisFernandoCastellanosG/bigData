"""
Author      : Luis Fernando Castellanos Guarin
Date        : 2025-03-06
Description :  Clase para almacenar variables de configuración constantes.
"""
class Config:
    
    # Rutas de carpetas
    RUTA_DATOS = "/home/usuario/datos"
    RUTA_MODELOS = "/home/usuario/modelos"
    RUTA_LOGS = "/home/usuario/logs"

    # Rutas de APIs
    API_USUARIOS = "https://api.ejemplo.com/usuarios"
    API_PRODUCTOS = "https://api.ejemplo.com/productos"
    API_CLIMA = "https://api.ejemplo.com/clima"

    # Otras constantes
    VERSION = "1.0.0"
    TASA_IMPUESTOS = 0.16
    TIMEOUT_CONEXION = 10  # segundo