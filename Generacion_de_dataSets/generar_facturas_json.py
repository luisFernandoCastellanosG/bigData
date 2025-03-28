# Autor: Luis Fernando Castellanos Guarin
# Fecha: 2024-03-19
# Descripción: Script para generar facturas en formato JSON con datos aleatorios.

import json
import random
import datetime

def generar_codigo_alfanumerico(longitud=10):
    caracteres = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(caracteres) for _ in range(longitud))

def generar_factura(empresa_nit, empresa_nombre, fecha_inicio_str, fecha_fin_str, factura_num_actual):
    ciudades = ["BOGOTA", "MEDELLIN", "BUCARAMANGA", "CALI", "BARRANQUILLA", "TUNJA"]
    sedes = ["sede A", "sede B", "sede C"]
    pagos = ["EFECTIVO", "TAR.CREDITO", "TAR.DEBITO", "TRANFERENCIA"]
    ivas = [0, 5, 19]

    fecha_inicio = datetime.datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
    fecha_fin = datetime.datetime.strptime(fecha_fin_str, '%Y-%m-%d')

    tiempo_inicio = datetime.time(0, 0, 0)
    tiempo_fin = datetime.time(23, 59, 59)

    fecha_hora_inicio = datetime.datetime.combine(fecha_inicio.date(), tiempo_inicio)
    fecha_hora_fin = datetime.datetime.combine(fecha_fin.date(), tiempo_fin)

    timestamp_inicio = fecha_hora_inicio.timestamp()
    timestamp_fin = fecha_hora_fin.timestamp()

    timestamp_random = random.uniform(timestamp_inicio, timestamp_fin)
    fecha_hora_aleatoria = datetime.datetime.fromtimestamp(timestamp_random).strftime('%Y-%m-%d %H:%M:%S')

    num_productos = random.randint(1, 20)
    productos = []
    for _ in range(num_productos):
        producto = {
            "codigo": generar_codigo_alfanumerico(),
            "total": random.randint(1, 20),
            "valor_unitario": random.randint(1000, 1000000),
            "descuento": round(random.uniform(0, 0.50), 2),
            "IVA": random.choice(ivas)
        }
        productos.append(producto)

    factura = {
        "empresa_nit": empresa_nit,
        "empresa_ciudad": random.choice(ciudades),
        "empresa_sede": random.choice(sedes),
        "empresa_nombre": empresa_nombre,
        "fecha_hora": fecha_hora_aleatoria,
        "factura_num": f"{factura_num_actual:05d}",
        "ciente_numero": random.randint(5000000, 1000000000),
        "pago_tipo": random.choice(pagos),
        "productos": productos
    }
    return factura

if __name__ == "__main__":
    try:
        rutaJson="Generacion_de_dataSets\facturas"
        n_facturas = int(input("Ingrese la cantidad de facturas a generar: "))
        empresa_nit_input = int(input("Ingrese el NIT de la empresa: "))
        empresa_nombre_input = input("Ingrese el nombre del supermercado: ")
        fecha_inicio_input = input("Ingrese la fecha de inicio del rango de facturación (YYYY-MM-DD): ")
        fecha_fin_input = input("Ingrese la fecha de fin del rango de facturación (YYYY-MM-DD): ")

        for i in range(1, n_facturas + 1):
            factura_data = generar_factura(empresa_nit_input, empresa_nombre_input, fecha_inicio_input, fecha_fin_input, i)
            nombre_archivo = rutaJson+"/factura_"+str(i)+".json"
            with open(nombre_archivo, 'w') as archivo_json:
                json.dump(factura_data, archivo_json, indent=4)
            print(f"Se ha creado el archivo: {nombre_archivo}")

        print("Proceso de creación de facturas finalizado.")

    except ValueError:
        print("Error: Por favor, ingrese un número entero válido para la cantidad de facturas y el NIT.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")