#Autor      : Luis Fernando Castellanos (Luisfc@corteconstitucional.gov.co)
#fecha      : 2025-mayo-28
#descripcion:   1- recorre todas las carpetas y subcarpetas de "C:\Users\luisfc\Documents\libros" donde hay archivo en formato pdf,epub, mobi  
#               2- lee cada archivo y extraer el texto teniendo presente que puede estar en español latino
#               3-crear un archivo json para cada archivo con la estructura {"nombre":"","autor":"","texto":""}

import os
from helpers.functions import functions
import json
from datetime import datetime

def main():
    # inicializo la clase funciones donde estan la atomización del codigo
    func = functions()
    
    # crear el directorio files_json en caso de no exitir
    output_dir = "D:/GIT/bigData/Generacion_de_dataSets/GenerarJson_documentos/files_json/"
    func.crear_carpeta(output_dir)
    
    # directorio donde estan los documentos/libros
    source_dir = r"C:/Users/luisfc/Documents/libros"
    
    # Counter for processed files
    totArchivos = func.contar_archivos_json(output_dir)
    numFile     = totArchivos
    print('en la carpeta [',output_dir,'], existen ',totArchivos,' archivos Json')
    # recorrer cada directorio y subdirectorio
    list_errores    = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            # validar los archivos permitidos
            if file.lower().endswith(('.pdf', '.epub', '.mobi')):
            #if file.lower().endswith(('.pdf')):
                file_path = os.path.join(root, file)
                numFile+=1
                # Extraer el contenido del archivo
                resultado = func.extraer_contenido_archivo(file_path)
                #print(file_path,'RESULTADO:',resultado)
                # verfica que haya extraido el contenido del archivo
                if resultado['estado'] == 'OK' and len(resultado['Contenido']) > 10:
                    totArchivos += 1
                    
                    # Crea estructura JSON
                    json_data = {
                        "id": str(totArchivos),
                        "nombre": file,
                        "fecha_generado": datetime.now().strftime("%Y-%m-%d"),
                        "Categoria": os.path.basename(root),  
                        "texto": resultado['Contenido']
                    }
                    
                    # Crea archivo JOSN 
                    output_file = os.path.join(output_dir, f"{totArchivos}.json")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, ensure_ascii=False, indent=4)
                    
                    print(f"Procesado  {totArchivos}: {file}")
                else:
                    list_errores.append([{'numFile':numFile,'file_path':file_path,'Error':resultado['mensaje']}])
    
    if (len(list_errores)>0):
        print('-----------SE PRESENTARON',len(list_errores) ,' ERRORES----------')
        print('VER ARCHIVO: ','documentos_con_errores.json')
        with open('documentos_con_errores.json', 'w', encoding='utf-8') as f:
            json.dump(list_errores,f,sort_keys = True, indent = 4,ensure_ascii = False)


if __name__ == "__main__":
    main()