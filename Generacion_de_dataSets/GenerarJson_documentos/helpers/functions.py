import re
import os
import time
import json
from datetime import datetime, timezone
import unicodedata
import shutil
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from PyPDF2 import PdfReader
from pathlib import Path
import chardet
from  helpers.OCR_pdf import OCR_pdf

class functions:
    def __init__(self):
        self.show_print=True
        self.arra_resuelvePrincipal=['administrando justicia en nombre del pueblo y por mandato de la Constitucion',
                                    'administrando justicia en nombre del pueblo',
                                    'administrando justicia',
                                    'en nombre del pueblo y por mandato',
                                    'en merito de lo expuesto, la corte constitucional'                            ]
        self.array_resuelveSecundario=['r e s u e l v e','r e s u e l ve','en merito de lo expuesto','resuelve','d e c i s i o n','decision','falla','f a l l a','fallo','f a l l o' ]
        self.meses = {
                        "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
                        "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
                        "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
                    }
        # Patrón para buscar fechas en un texto
        self.patron_fecha  = r"(\d{1,2})\s+de\s+([a-zA-Z]+)\s+(?:del\s+|de\s+)?(\d{4})?"   # DIA - MES - AÑO
        self.patron2_fecha = r"([a-zA-Z]+)\s+(\d{1,2})\s+(?:del|de)\s+(\d{4})"             # MES - DIA - AÑO
        self.patron3_fecha = r"(\d{4})\s+([a-zA-Z]+)\s+(\d{1,2})"                          # AÑO - MES - DIA
        # Patrones para fechas
        self.patrones = [
                            r"(\d{4})\s+([a-zA-Z]+)\s+(\d{1,2})",  # AÑO - MES - DIA
                            r"([a-zA-Z]+)\s+(\d{1,2})\s+(?:del|de)\s+(\d{4})",  # MES - DIA - AÑO
                            r"(\d{1,2})\s+de\s+([a-zA-Z]+)\s+(?:del\s+|de\s+)?(\d{4})?",  # DIA - MES - AÑO
                            r"(\d{1,2})\s+([a-zA-Z]+)\s+(\d{4})"  # DIA - MES - AÑO sin "de"
                        ]

    #----------funciones para manejo de fechas/horas/minutos/segundos---------------------
    # Función para calcular la diferencia en minutos entre dos fechas
    def calcular_diferencia_minutos(fecha_inicial, fecha_final):
        # Calcular la diferencia en minutos
        diferencia = fecha_final - fecha_inicial
        diferencia_minutos = diferencia.total_seconds() / 60
        
        return diferencia_minutos
    #----------funciones para manejo de arrays---------------------
    def buscar_en_array_por_columna(self,array, columna,valorBuscado):
        for indice, fila in array.iterrows():
            if str(fila[columna]) == str(valorBuscado): # Acceder a la columna con el nombre
                return fila  # Retornar la fila completa (Series)
    
    #----------Funciones para manejo de textos y caracteres-------------
    def es_numerico(self,valor):
        return valor.isdigit() if isinstance(valor, str) else False
    
    def buscar_posNumericInTxt(self,texto):   #@Description:retorna la posicion del primer número que encuentre en un texto
        match = re.search(r'[0-9]', texto)
        if match:
            pos = match.start()
        else:
            pos = False
        return pos
    
    def eliminar_especiales_extremos(self, texto):
        """Elimina caracteres especiales de la primera y última letra de cada palabra en un texto.
            Arg:texto   : El texto a procesar.
            Returns     :Una cadena con los caracteres especiales eliminados de los extremos de cada palabra."""
        patron = r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$'
        # Reemplazar los caracteres encontrados por una cadena vacía
        texto_limpio = re.sub(patron, '', texto)
        return texto_limpio
    
    def contar_y_ubicar_frase(self,texto, frase):
        
        # Convertir tanto el texto como la frase a minúsculas y quitar tildes
        #texto_normalizado = unicodedata.normalize('NFKD', texto.lower())
        #frase_normalizada = unicodedata.normalize('NFKD', frase.lower())
        #texto= unidecode(texto).lower()
        #frase= unidecode(frase).lower()
        #print('____DEF: contar_y_ubicar_frase___\n, BUSCAR [',frase,']\nTEXTO [',texto[:200],']')
        # Eliminar caracteres que no sean letras o espacios
        #texto_limpio = re.sub(r'[^a-zA-Z\s]', '', texto_normalizado)
        #frase_limpia = re.sub(r'[^a-zA-Z\s]', '', frase_normalizada)
        #texto_limpio = texto_normalizado
        #frase_limpia = frase_normalizada

        # Buscar todas las ocurrencias y guardar sus posiciones iniciales
        posiciones = [m.start() for m in re.finditer(frase, texto)]

        return posiciones

    def validar_texto_con_providencias(self, texto,separador=','):
        nueva_lista=[]
        texto      =texto.upper()
        palabras_a_reemplazar = ["SENTENCIA","ARCHIVO","DICIEMBRE","N°"]
        for palabra in palabras_a_reemplazar:
            texto = texto.replace(palabra, "")
        texto = texto.replace("AUTO", ",A")
        
        lista_providencias = texto.replace("Y",",").replace(";",",").split(separador)         # Convertir el texto en una lista usando el separador 
        lista_providencias = [palabra for palabra in lista_providencias if len(palabra) >= 5]
        #print('-------LISTADO PROVIDENCIAS=> ',lista_providencias,'---------')
        #for providencia in lista_providencias:
        for i in range(len(lista_providencias)):            # Recorrer cada palabra de la lista
            #print('providencia a validar:',lista_providencias[i].upper(),'---------------\n')
            providencia=self.eliminar_especiales_extremos(lista_providencias[i])
            providencia=providencia.replace("DEL", "/").replace("DE", "/").replace(" ", "").strip()
            #print('providencia limpia:',providencia,'---------------\n')
            
            if(providencia[0:1]=='A'):
                """if(providencia[1:1].isnumeric()==True):
                    providencia='A. '+ providencia[1:]
                elif(providencia[1:1]=='-'):
                    providencia='A. '+ providencia[2:]"""
                providencia=self.reemplazar_inicio_providencia(providencia,"A. ")
                if(providencia[0:3]=='A. '):
                    providencia='A. '+providencia[3:].replace("-","/")
            elif providencia[0:1]=='T':
                if(providencia[1:1].isnumeric()==True):
                    providencia='T-'+ providencia[1:]
                if providencia[1:1]!='-':
                    providencia='T-'+providencia[2:].replace("-","/")
            elif providencia[0:2]=='SU':
                """if(providencia[2:1].isnumeric()==True):
                    providencia='SU.'+ providencia[3:]
                elif(providencia[2:1]=='-'):
                    providencia='SU.'+ providencia[3:]"""
                providencia=self.reemplazar_inicio_providencia(providencia,"SU.")
                if(providencia[0:3]=='SU.'):
                    providencia='SU.'+providencia[3:].replace("-","/")
            elif providencia[0:2]=='C':
                if(providencia[1:1].isnumeric()==True):
                    providencia='C-'+ providencia[1:]
                if(providencia[0:2]=='C-'):
                    providencia='C-'+providencia[3:].replace("-","/")

            if ("/" in providencia):                         #si despues de validar esta el / haga   
                partes       = providencia.split('/')        # Dividimos el texto por el '/'
                #print('partes-->[',providencia,']',partes)
                anio_parcial = partes[1]
                if len(anio_parcial)>1 and anio_parcial.isdigit():                   # Verificamos si la parte extraída es numérica
                    if len(anio_parcial) == 4:               # Completamos el año según la longitud
                        anio_parcial=anio_parcial[2:]
                nueva_lista.append(partes[0] + "/" + anio_parcial) # Reconstruimos el texto con el año completo
            
        return nueva_lista
    
    def reemplazar_inicio_providencia(self,texto,textoInicio):
        """Reemplaza todo lo anterior al primer número en un texto por "SU."
            Args:texto: El texto a modificar.
            Returns:El texto modificado."""
        for i, char in enumerate(texto):
            if char.isdigit():
                return textoInicio + texto[i:]
        return textoInicio + texto  # Si no encuentra ningún número, agrega "SU." al final
    
    def f_encontrar_palabras(self,cadena, palabras,posicionIniBase = 0, posMaxima=-1,primeraOpcion=False):
        x           =0
        posiciones  =[]
        textLen     =len(cadena)
        encontrado =False
        if self.show_print==True:print('****f_encontrar_palabras: textLen-->',textLen,', posicionIni:',posicionIniBase,', posMaxima:',posMaxima,',primeraOpcion:',primeraOpcion)
        while x<len(palabras) and encontrado==False:
            posicionIni =posicionIniBase
            y           =0
            posFind     =-1
            #if self.show_print==True:print(y,'-->buscando:',palabras[x])
            while posicionIni<textLen and y<10:
                if (posMaxima>0):
                    posFind = cadena.rfind(palabras[x],posicionIni,posMaxima)
                else:
                    posFind = cadena.rfind(palabras[x],posicionIni)
                if posFind != -1:
                    posicionIni=posFind+10
                    if primeraOpcion==True:
                        encontrado=True
                    if self.show_print==True:print()
                    if posMaxima>0 and  posFind<posMaxima and posFind>(posicionIniBase*2):
                        posiciones.append(posFind)
                else:
                    match = re.search(palabras[x], cadena[posicionIni:], re.IGNORECASE)
                    if match:
                        posFind=match.start()
                        if self.show_print==True:print(palabras[x],', hice match en:',posFind)
                    posicionIni=textLen
                y+=1
                if self.show_print==True:
                    if posFind != -1:
                        print('(',x,')[',palabras[x],'], posicionIni:',posicionIni,',posMaxima:',posMaxima,', posFind:',posFind,',van:',len(posiciones),'[[',cadena[posFind:(posFind+100)].rstrip("\n"),']]')
                    else:
                        print('(',x,')[',palabras[x],'], posicionIni:',posicionIni,',posMaxima:',posMaxima,', posFind:',posFind,',van:',len(posiciones))
            x+=1    
        return posiciones

    def f_encontrar_fin_resuelve(self, texto,posIni = 0):
        if self.show_print==True:print('_______________*****f_encontrar_fin_resuelve******_______________')
        palabras    =['copiese, publiquese, comuniquese',
                    'copiese, publiquese',
                    'copiese, notifiquese',
                    'copiese, comuniquese',
                    'notifiquese, comuniquese, cumplase',
                    'notifiquese, comuniquese', 
                    'Notifiquese y comuniquese',
                    'notifiquese y cumplase',
                    'notifiquese, publiquese y cumplase',
                    'comuniquese, publiquese y cumplase',
                    'Notifiquese, comuniquese y cumplase',
                    'comuniquese y cumplase',
                    'publiquese y cumplase',
                    'insertese en la gaceta de la corte constitucional',
                    'secretaria general',
                    'secretario general',
                    'secrtaria general',
                    'presidente de la sala',
                    'aclaracion de voto','salvamento de voto',
                    'copiese','notifiquese','notifiquese','secretaria']
        x           =0
        textLen     =len(texto)
        textLen50   =round(textLen/2)
        encontroFin =False
        posFind     =-1
        while encontroFin==False and x<len(palabras):
            posFind=texto.rfind(palabras[x],posIni)
            if posFind == -1:
                match = re.search(palabras[x], texto, re.IGNORECASE)
                if match:
                    posFind=match.start()
                    if self.show_print==True:print(palabras[x],', hice match en:',match.start())
            if posFind!=-1 and posFind>(posIni*2):
                encontroFin=True
            if self.show_print==True:print(x,'/',len(palabras),'[',palabras[x],'],posIni:',posIni,', 50%:',textLen50,',POSFIN:',posFind,',encontroFin:',encontroFin)
            x+=1
        if self.show_print==True:print("posFind:[",posFind,"]____texto del fin del resuelve:\n[[",texto[(posFind-30):(posFind+100)].rstrip("\n"),']]')
        return posFind

    def f_buscar_pos_base(self,texto,textBuscado='', posIni=0):
        #si es una sentencia (C, SU y T) posiblemente inicie con "administrando justicia en nombre del pueblo"
        if self.show_print==True:print('____f_buscar_pos_base___',textBuscado,', desde ',posIni)
        x=0
        posFin=0
        encontroFin =False
        while encontroFin!=True and x<1:
            posFin=texto.find(textBuscado,1)
            match = re.search(textBuscado, texto, re.IGNORECASE)
            if match:
                posFin=match.start()
                encontroFin=True
                #if self.show_print==True:print('textBuscado:[[',textBuscado,']], hice match en:',posFin,texto[posFin:(posFin+10)].rstrip("\n"))
            x+=1
            
        return posFin
    
    def buscar_posicion_ultimo_separador(self,texto):
        """ Busca la posición del último '/' o '-' en un texto, de derecha a izquierda.
            Args:texto (str): El texto en el que se buscará.
            Returns:int: La posición del último '/' o '-', o -1 si no se encuentra ninguno.
        """
        for i in range(len(texto) - 1, -1, -1): # recorre el texto de derecha a izquierda
            if texto[i] == '/' or texto[i] == '-':
                return i
        return -1  # Retorna -1 si no se encuentra ningún separador

    def f_main_extraer_resuelve(self,texto):
        textResuelve    = ''
        lenTexto        = len(texto)
        textoUnicode    = unidecode(texto)
        textoMinuscula  = textoUnicode.lower()      #vuelva minuscula el texo   

        posInicial      = self.f_buscar_pos_base(texto,'bogot')                                                                   
        if (posInicial<0 or (posInicial>0 and posInicial>(len(textoMinuscula)/2))):
            posInicial=0
        posFinResuelve  = self.f_encontrar_fin_resuelve(textoMinuscula,posInicial)                                                #traiga la posición final de texto hasta el comuniquese y cumplase pero a partir de la posición del resuelve
        if (posFinResuelve<0):posFinResuelve=len(texto)
        listResuelve    = self.f_encontrar_palabras(textoMinuscula,self.arra_resuelvePrincipal,posInicial,posFinResuelve)          #Busque cuantas veces aparece la palabra resuelve
        if len(listResuelve)==0:
            listResuelve    = self.f_encontrar_palabras(textoMinuscula,self.array_resuelveSecundario,posInicial,posFinResuelve,True)       #sino entro la palabra resuelve busque otras posibles opciones
        if len(listResuelve)==1:                                                                                #si solo esta una vez la palabra resuelve o su similares, traiga el texto hasta el comuniquese y cumplase
            if (posFinResuelve>0):
                textResuelve        =texto[listResuelve[0]:posFinResuelve]    
            else:
                textResuelve        =texto[listResuelve[0]:]                     
        else:
            posFinResuelveTmp   =0
            posIniResuelve      =0
            distancia           =-1
            numResuelve         =1
            for posResuelve in listResuelve:                                                                    #si aparece más de una vez la palabra RESUELVE        
                if (posFinResuelve!=-1):                                                                        #si existe un fin del resuelve osea donde esta el comuniquese o complase
                    if(posFinResuelveTmp==0):
                        posFinResuelveTmp   =posFinResuelve
                        distancia           =posFinResuelve-posResuelve
                        posIniResuelve      =posResuelve
                    if (distancia> (posFinResuelve-posResuelve)):                                               #el que tenga la distancia más corta es el texto del resuelve
                        distancia           =posFinResuelve-posResuelve
                        posIniResuelve      =posResuelve
                        posFinResuelveTmp   =posFinResuelve
                if self.show_print==True:print('(',numResuelve,'): posResuelve:',posResuelve,', posFinResuelve:', posFinResuelve,', posFinResuelveTmp:',posFinResuelveTmp,', distancia:',distancia,' =[[',texto[posResuelve:posResuelve+100].rstrip("\n"),']]')
                numResuelve+=1
            if self.show_print==True:print('posIniResuelve:',posIniResuelve,',posFinResuelveTmp:',posFinResuelveTmp,', posFinResuelveTmp:',posFinResuelveTmp,'==',posFinResuelve)                            
            if (posFinResuelveTmp>0):                                                                          #traiga el texto desde el resuelve hasta el final de que tenga la distancia más corta     
                textResuelve        =texto[posIniResuelve:posFinResuelveTmp]
        if self.show_print==True:print('\n RESUELVE:::::\n',textResuelve)
        return textResuelve
    
    def f_extraer_texto_resuelve(self, texto, posIni=0,PosFinResuelve=-1):
        textResuelve=''
        if (PosFinResuelve==-1):
            PosFinResuelve=self.f_encontrar_fin_resuelve(texto,posIni)
            if PosFinResuelve!=-1:
                textResuelve=texto[posIni:PosFinResuelve]
        if self.show_print==True:print('posIni',posIni,', posfin:',PosFinResuelve,'--->',textResuelve)
        if len(textResuelve)==0:   #en caso que no se pueda encontrar el fin del RESUELVE, vaya y busque los nombre de los magistrados

            textResuelve=texto[posIni:]   
            #print('NO ENCONTREEEEEE: ',textResuelve)     
        #  quitar los saltos dobles de linea 
        textResuelve=textResuelve.replace('\n\n\n','\n')
        textResuelve=textResuelve.replace('\n\n','\n')
        #textResuelve = ''.join(e for e in textResuelve if (e==' ' or e=='.' or e==':' or e.isalnum()))
        return textResuelve
    
    def extraer_tres_fecha_de_texto_con_patron(self,texto):
        """
        Extrae y retorna un diccionario con las fechas en el texto según las referencias: auto, notificado y vencimiento.
        """
        # Normalizar texto para casos especiales

        texto = self.normalizar_texto_para_fechas(texto)
        # Patrones para identificar segmentos de texto
        patron_auto = r"^(.*?)(?=notificado|vencimiento|$)"
        patron_notificado = r"notificado(.*?)(?=vencimiento|$)"
        patron_vencimiento = r"vencimiento(.*)$"

        # Patrones para fechas
        

        # Extraer segmentos del texto
        segmento_auto = re.search(patron_auto, texto, re.IGNORECASE)
        segmento_notificado = re.search(patron_notificado, texto, re.IGNORECASE)
        segmento_vencimiento = re.search(patron_vencimiento, texto, re.IGNORECASE)

        # Año de referencia para casos especiales
        referencia_anio = None
        if segmento_vencimiento:
            fecha_vencimiento = re.search(self.patron_fecha, segmento_vencimiento.group(), re.IGNORECASE)
            if fecha_vencimiento and fecha_vencimiento.group(3):
                referencia_anio = fecha_vencimiento.group(3)
        
        # Extraer fechas
        fecha_auto          = self.buscar_fecha(segmento_auto, referencia_anio)
        fecha_notificado    = self.buscar_fecha(segmento_notificado, referencia_anio)
        fecha_vencimiento   = self.buscar_fecha(segmento_vencimiento, referencia_anio)

        # Ajustar años en casos especiales
        if referencia_anio:
            if not fecha_auto:
                if "diciembre" in (segmento_auto.group() if segmento_auto else "") and "enero" in (segmento_vencimiento.group() if segmento_vencimiento else ""):
                    referencia_anio_auto = str(int(referencia_anio) - 1)
                    fecha_auto           = self.buscar_fecha(segmento_auto, referencia_anio_auto)
                    fecha_notificado     = self.buscar_fecha(segmento_notificado, referencia_anio_auto)
            if not fecha_vencimiento:
                fecha_vencimiento = self.buscar_fecha(segmento_vencimiento, referencia_anio)
        
        return {
            "auto": fecha_auto,
            "notificado": fecha_notificado,
            "vencimiento": fecha_vencimiento
        }
    
    def extraer_expedientes_de_texto(self, texto):
        """
        Extrae los números de expediente en formato 'TXXXXXXX' de un texto dado.
        :param texto: Texto en el que buscar los expedientes.
        :return: Lista con los números de expediente encontrados.
        """
        # Elimina caracteres no deseados y unifica formato de los expedientes
        texto_limpio = texto.replace('-', '').replace('_', '').replace('.', '').upper()
        
        
        # Busca coincidencias de expedientes con prefijo 'T' seguido de dígitos
        #expedientes = re.findall(r'T\d+', texto_limpio)
        expedientes = re.findall(r'(T|\d+)', texto_limpio)
        # Agrega el prefijo 'T' a los números que no lo tengan
        expedientes = ['T' + exp for exp in expedientes if exp.isdigit()]
        
        return expedientes   
    
    def quitar_saltos_de_linea(self,texto):
        # Reemplaza múltiples saltos de línea consecutivos con un solo salto de línea
        return "\n".join(linea.strip() for linea in texto.splitlines() if linea.strip())   
    
    def quitar_espacios_multiples(self,texto):
        # Reemplaza múltiples espacios consecutivos con un solo espacio
        return re.sub(' +', ' ', texto)
    
    def quitar_etiquetas_html_php(self,texto):
        """
        Quita las etiquetas HTML y PHP de un texto.
        """
        # Expresión regular para etiquetas HTML y PHP
        patron_etiquetas = re.compile(r"<[^>]+>|<\?.+?\?>", flags=re.DOTALL)

        # Reemplaza las etiquetas por espacios en blanco
        texto_limpio = patron_etiquetas.sub("", texto)
        # Reemplazar &nbsp; por espacio
        patron_nbsp = r'&nbsp;'
        texto_limpio = re.sub(patron_nbsp, ' ', texto_limpio)
        # Reducir saltos de línea múltiples a uno
        patron_saltos_linea = r'\n+'
        texto_limpio = re.sub(patron_saltos_linea, '\n', texto_limpio)
        #print("________TEXTO ORIGINAL:______\n",texto,"________TEXTO LIMPIO:______\n",texto_limpio)

        return texto_limpio
    
    def webScrapingCorte(self, UrlWeb):
        """ Extrae el texto de una página web dada su URL.
        Args: UrlWeb (str): La URL de la página web de la cual se extraerá el texto.
        Returns:str: El texto extraído de la página web.
        """
        try:
            response = requests.get(UrlWeb)
            response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP malos (4XX o 5XX)
            html_content = response.text
            return self.extraer_texto_de_html(html_content)
        
        except requests.exceptions.RequestException as e:
            return f"Error al acceder a la URL: {e}"
        
    def extraer_texto_de_html(self, html):
            """Extrae el texto de un archivo HTML y lo devuelve como una cadena."""
            soup = BeautifulSoup(html, 'html.parser')
            texto = soup.get_text(separator='\n', strip=True)
            return texto

    
    def buscar_fecha(self,segmento, referencia_anio=None):
        """
        Busca y devuelve la primera fecha válida en un segmento de texto.
        Si el año no está presente, usa referencia_anio cuando sea necesario.
        """
        #print("buscar_fecha en:[",segmento.group(),"],referencia_anio:",referencia_anio)
        if not segmento:
            return ""
        """
        fechas = re.findall(self.patron_fecha, segmento.group(), re.IGNORECASE)
        if fechas:
            for dia, mes, anio in fechas:
                mes_numero = self.meses.get(mes.lower())
                if mes_numero:
                    if not anio:
                        anio = referencia_anio
                    if anio:
                        return f"{anio}-{mes_numero}-{dia.zfill(2)}"
        else:# patron 2 
            fechas = re.findall(self.patron2_fecha, segmento.group(), re.IGNORECASE)
            #print("patron 2=",fechas)
            if fechas:
                for mes,dia, anio in fechas:
                    mes_numero = self.meses.get(mes.lower())
                    if mes_numero:
                        if not anio:
                            anio = referencia_anio
                        if anio:
                            return f"{anio}-{mes_numero}-{dia.zfill(2)}
            else:# patron 3
                fechas = re.findall(self.patron3_fecha, segmento.group(), re.IGNORECASE)
                if fechas:
                    for mes,dia, anio in fechas:
                        mes_numero = self.meses.get(mes.lower())
                        if mes_numero:
                            if not anio:
                                anio = referencia_anio
                            if anio:
                                return f"{anio}-{mes_numero}-{dia.zfill(2)}"""
                
        for patron in self.patrones:
            coincidencia = re.search(patron, segmento.group(), re.IGNORECASE)
            #print(",\nFechas:[",coincidencia,"]")
            if coincidencia:
                grupos = coincidencia.groups()
                if len(grupos) == 3:
                    if patron == self.patrones[0]:  # AÑO - MES - DIA
                        anio, mes, dia = grupos
                    elif patron == self.patrones[1]:  # MES - DIA - AÑO
                        mes, dia, anio = grupos
                    elif patron == self.patrones[2]:  # DIA - MES - AÑO
                        dia, mes, anio = grupos
                    elif patron == self.patrones[3]:  # DIA - MES - AÑO
                        dia, mes, anio = grupos

                    mes_numero =self.meses.get(mes.lower())
                    if mes_numero:
                        if not anio:
                            anio = referencia_anio
                        if anio:
                            return f"{anio}-{mes_numero}-{dia.zfill(2)}"""
        
        return ""
    
    def normalizar_texto_para_fechas(self,texto):
        """
        Separa las palabras pegadas a los meses en un texto dado.

        Args:
            texto: El texto a procesar.
            meses: Un diccionario con los nombres de los meses y sus abreviaturas numéricas.

        Returns:
            El texto con las palabras separadas correctamente.
        """        
        #print("TEXTO ENTRADA =>",texto)
        #texto = texto.lower()
        # Convertir el texto a minúsculas para facilitar la comparación
        # Expresión regular para encontrar números seguidos o precedidos de caracteres
        texto = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', texto.lower())  # Número seguido de letra
        texto = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', texto)  # Letra seguida de número
        # Separar palabras de meses pegadas (ejemplo: "marzode" => "marzo de")
        for mes in  self.meses.keys():
            texto = re.sub(rf'({mes})(de)', r'\1 \2', texto)

        # Iterar sobre los meses y sus abreviaturas
        """for mes, abreviatura in self.meses.items():
            # Buscar patrones como "mespalabra" o "abreviaturapalabra"
            texto = re.sub(rf"({mes}|\b{abreviatura})\b", r"\1 ", texto)
            # Buscar patrones como "palabrames" o "palabraabreviatura"
            texto = re.sub(rf"\b({mes}|\b{abreviatura})", r" \1", texto)"""

        # Eliminar espacios en blanco adicionales
        texto = re.sub(r"\s+", " ", texto).strip()
        #print("TEXTO NUEVO =>",texto)

        return texto
    
    #------------------- funciones para manejo de archivos y carpetas-----------
    def obtener_subdirectorios(self,ruta_principal):
        """Obtiene una lista de todos los subdirectorios dentro de una ruta dada.

        Args:
            ruta_principal (str): La ruta del directorio principal desde donde iniciar la búsqueda.

        Returns:
            list: Una lista de cadenas, donde cada cadena representa la ruta completa de un subdirectorio.
        """
        subdirectorios = []
        for root, dirs, files in os.walk(ruta_principal):
            for dir in dirs:
                ruta_completa = os.path.join(root, dir)
                subdirectorios.append(ruta_completa)
        return subdirectorios
    
    def obtener_lista_elementos(self, ruta):
        """
        Esta función retorna una lista con los nombres de los archivos y subdirectorios
        en una ruta dada.

        Args:
            ruta: La ruta del directorio a explorar.

        Returns:
            Una lista con los nombres de los archivos y subdirectorios.
        """
        lista_elementos = []
        for elemento in os.listdir(ruta):
            ruta_completa = os.path.join(ruta, elemento)
            if os.path.isdir(ruta_completa):
                fecha_modificacion = time.ctime(os.path.getmtime(ruta_completa))
                lista_elementos.append({'nombre': elemento, 'tipo': 'directorio','ruta':ruta_completa,'fecha_modificacion': fecha_modificacion,'hijos':self.obtener_lista_elementos(ruta_completa)})
            else:
                nombre, extension = os.path.splitext(elemento)
                fecha_modificacion = time.ctime(os.path.getmtime(ruta_completa))
                lista_elementos.append({'nombre': nombre, 'tipo': 'archivo','ruta':ruta_completa, 'extension': extension[1:], 'fecha_modificacion': fecha_modificacion})
        return lista_elementos

    def validar_y_borrar_ruta(self,ruta):
        """verificar si carpeta existe,sino: crearla, si existe: Borra todos los archivos y carpetas de una ruta.
            Parámetros:ruta (str): La ruta a la carpeta que se desea eliminar."""
        if os.path.exists(ruta):
            for raiz, directorios, archivos in os.walk(ruta):
                for archivo in archivos:
                    os.remove(os.path.join(raiz, archivo))
                for directorio in directorios:
                    os.rmdir(os.path.join(raiz, directorio))
        else:
            os.makedirs(ruta)
            print(f"Se creó la carpeta {ruta}.")
                
    def crear_archivo_json(self,filename,dataFileJson):
        with open(filename, 'w', encoding='utf-8') as f:                             #guarde por cada año un json con archivos TXT a los que no se les pudo extraere  el resuelve
            json.dump(dataFileJson,f,sort_keys = True, indent = 4,ensure_ascii = False)
    
    def contar_archivos_json(self, ruta):
        dirpath = Path(ruta)
        archivos_json = list(dirpath.glob("*.json"))
        return len(archivos_json)
    
    def guardar_contenido_en_txt(contenido, ruta_archivo):
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as archivo_txt:
                archivo_txt.write(contenido)
            return f"Contenido guardado en {ruta_archivo}"
        except Exception as e:
            return f"Error al guardar el contenido en el archivo: {str(e)}"   
    
    def copiar_archivo(self, rutaArchivo, rutaDestino):
        """Copia un archivo a un destino si existe."""
        estado=""
        if os.path.exists(rutaArchivo):
            try:
                shutil.copy2(rutaArchivo, rutaDestino)
                #print(f"Archivo {rutaArchivo} copiado a {rutaDestino} exitosamente.")
                estado="copiado"
            except shutil.Error as e:
                #print(f"Error al copiar el archivo: {e}")
                estado="ERROR al copiar el archivo: {e}"
        else:
            #print(f"El archivo {rutaArchivo} no existe.")
            estado="ERROR El archivo ["+rutaArchivo+"] NO existe."
        return estado
    
    def eliminar_archivo(self,ruta_archivo):
        """Elimina un archivo si existe."""

        if os.path.exists(ruta_archivo):
            try:
                os.remove(ruta_archivo)
            except OSError as e:
                print(f"Error al eliminar el archivo: {e}")
        else:
            print(f"El archivo {ruta_archivo} no existe.")
    
    def extraer_contenido_archivo(self,ruta_archivo):
        try:
            with open(ruta_archivo, 'rb') as f:
                rawdata = f.read()
            result_encoding     = chardet.detect(rawdata)
            if (result_encoding['encoding']!=None):
                archivo_encoding    = result_encoding['encoding']
            else:
                archivo_encoding='utf-8'
            extension = os.path.splitext(ruta_archivo)[1].lower()
            if extension == '.pdf':
                # intentar extraer texto de forma basica usando PdfReader
                contenido =self.convertir_pdf_a_texto(ruta_archivo,archivo_encoding).strip()
                print(ruta_archivo,'=>',archivo_encoding,'=>tamaño',len(contenido))
                if len(contenido) < 10:
                    # si falla la extración de texto se usara OCR
                    self.OCR_pdf   = OCR_pdf()
                    contenido=self.OCR_pdf.extraerImagenesTextoPDF(ruta_archivo) 
            
            elif extension == '.epub':
                try:
                    import ebooklib
                    from ebooklib import epub
                    from bs4 import BeautifulSoup
                    
                    book = epub.read_epub(ruta_archivo)
                    contenido = ""
                    
                    for item in book.get_items():
                        if item.get_type() == ebooklib.ITEM_DOCUMENT:
                            soup = BeautifulSoup(item.get_content(), 'html.parser')
                            contenido += soup.get_text() + "\n"
                            
                except Exception as e:
                    return {'estado': 'ERROR', 'mensaje': f'Error al procesar EPUB: {str(e)}', 'Contenido': ''}
            
            elif extension == '.mobi':
                try:
                    import mobi
                    import tempfile
                    import shutil
                    
                    # Create a temporary directory
                    tempdir = tempfile.mkdtemp()
                    try:
                        # Extract the mobi file
                        mobi.extract(ruta_archivo, tempdir)
                        
                        # Find the HTML file in the temp directory
                        html_file = None
                        for root, dirs, files in os.walk(tempdir):
                            for file in files:
                                if file.endswith('.html'):
                                    html_file = os.path.join(root, file)
                                    break
                            if html_file:
                                break
                        
                        if html_file:
                            with open(html_file, 'r', encoding='utf-8') as f:
                                soup = BeautifulSoup(f.read(), 'html.parser')
                                contenido = soup.get_text()
                        else:
                            return {'estado': 'ERROR', 'mensaje': 'No se encontró contenido HTML en el archivo MOBI', 'Contenido': ''}
                            
                    finally:
                        # Clean up the temporary directory
                        shutil.rmtree(tempdir)
                        
                except Exception as e:
                    return {'estado': 'ERROR', 'mensaje': f'Error al procesar MOBI: {str(e)}', 'Contenido': ''}
            
            else:
                return {'estado': 'ERROR', 'mensaje': 'Formato de archivo no soportado', 'Contenido': ''}
            
            # Clean up the content
            contenido = self.quitar_saltos_de_linea(contenido)
            contenido = self.quitar_espacios_multiples(contenido)
            #contenido = self.quitar_etiquetas_html_php(contenido)
            
            return {'estado': 'OK', 'mensaje': 'Archivo procesado correctamente', 'Contenido': contenido}
            
        except Exception as e:
            return {'estado': 'ERROR', 'mensaje': str(e), 'Contenido': ''}

    #---------------------funciones para trabajar con carpetas-----------------
    def crear_carpeta(self,ruta):
        """Elimina recursivamente todos los archivos y subcarpetas dentro de una carpeta.
            Args: ruta_carpeta: La ruta completa de la carpeta a eliminar. """
        try:
            if os.path.exists(ruta):
                print(f"La carpeta {ruta} existe exitosamente.")
            else:
                os.makedirs(ruta)
                print(f"No existia, Se creó la carpeta {ruta}.")
        except OSError as e:
            print(f"Error al eliminar la carpeta: {e}")

    def crear_carpeta_o_eliminar_contenido(self,ruta):
        """Elimina recursivamente todos los archivos y subcarpetas dentro de una carpeta.
            Args: ruta_carpeta: La ruta completa de la carpeta a eliminar. """
        try:
            if os.path.exists(ruta):
                shutil.rmtree(ruta, ignore_errors=False)
                # Creamos nuevamente la carpeta vacía
                os.mkdir(ruta)
                print(f"Contenido de la carpeta {ruta} eliminado exitosamente.")
            else:
                os.makedirs(ruta)
                print(f"No existia, Se creó la carpeta {ruta}.")
        except OSError as e:
            print(f"Error al eliminar la carpeta: {e}")

    #-----------------funciones para trabajar con archivos PDF [text o imagenes (OCR)]
    def convertir_pdf_a_texto(self, pdf_path, decode='utf-8'):
        try:
            # Open the PDF file
            reader = PdfReader(pdf_path)
            number_of_pages = len(reader.pages)
            print(pdf_path,'con ',number_of_pages,' paginas')
            # Initialize text content
            text_content = ""
            
            # Extract text from each page
            for page_num in range(number_of_pages):
                try:
                    # Get the page
                    page = reader.pages[page_num]
                    
                    # Extract text from the page
                    page_text = page.extract_text()
                    
                    # Add page text to content if it's not None
                    if page_text:
                        text_content += page_text + "\n"
                        
                except Exception as e:
                    print(f"Error extracting text from page {page_num + 1}: {str(e)}")
                    continue
            
            # If no text was extracted, try OCR
            if not text_content.strip():
                print("No text extracted, trying OCR...")
                return self.convertir_PDF_a_texto_con_OCR(pdf_path, decode)
            
            return text_content
            
        except Exception as e:
            print(f"Error converting PDF to text: {str(e)}")
            return ""
    
    

    def limpiar_consola(self):
        """Limpia la consola, adaptándose al sistema operativo."""
        if os.name == 'nt':  # Windows
            os.system('cls')
        else:  # Linux, macOS, etc.
            os.system('clear')

    def callAPI(URL, data):
        result      =None
        try:
            token       = "000000000000"
            headers     = {"x-api-key": f"{token}"}
            response    = requests.post(URL, headers=headers, json=data)
            if response.status_code == 200:
                #print('Data:', response.json())
                result=response.json()
            else:
                print('Error en la solicitud (',response.status_code,'), detalles:', response.text)
        except:
            print("algo salio mal con la API: ",URL,'\nData:',data)          
        return result
    #----------------------------------funciones para trabajar con array/listas----------------
    def strpos_arr(self,texto, array_letras):
        min_pos = -1
        if not isinstance(array_letras, list):
            array_letras = [array_letras]
        for letra in array_letras:
            pos = texto.upper().find(letra.upper())
            if pos != -1 and min_pos == -1:
                min_pos = pos
        return min_pos