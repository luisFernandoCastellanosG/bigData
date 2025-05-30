#Autor      : Luis Fernando Castellanos (Luisfc@corteconstitucional.gov.co)
#fecha      : 2025-marzo-11
#descripcion: permite usar OCR para extraer texto de archivos PDF escaneados
#pytesseract instalar la version local (windows)

import os
import time
import fitz             #funciona al instalar PyMuPDF
from PIL import Image
from pytesseract import pytesseract

class OCR_pdf:
    def __init__(self):
        """
        inicializa la libreria de OCR
        """
        self.tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"           #ruta donde quedo instalado 
        self.dimlimit       = 0  # 100  # each image side must be greater than this
        self.relsize        = 0  # 0.05  # image : image size ratio must be larger than this (5%)
        self.abssize        = 0  # 2048  # absolute image size limit 2 KB: ignore if smaller
        self.imgDir         = "D:/GIT/bigData/Generacion_de_dataSets/GenerarJson_documentos/Data_tmp@/"  # found images are stored in this subfolder
        pytesseract.tesseract_cmd = self.tesseract_path
        if not os.path.exists(self.imgDir):  # make subfolder if necessary
            os.mkdir(self.imgDir)
            print('____La carpeta [',self.imgDir,'] NO existía, fue necesario crearla___')
        for archivo in os.listdir(self.imgDir):
            ruta_archivo = os.path.join(self.imgDir, archivo)
            os.remove(ruta_archivo)
    
    def recoverpix(self, doc, item):
        xref = item[0]  # xref of PDF image
        smask = item[1]  # xref of its /SMask

        # special case: /SMask or /Mask exists
        if smask > 0:
            pix0 = fitz.Pixmap(doc.extract_image(xref)["image"])
            if pix0.alpha:  # catch irregular situation
                pix0 = fitz.Pixmap(pix0, 0)  # remove alpha channel
            mask = fitz.Pixmap(doc.extract_image(smask)["image"])

            try:
                pix = fitz.Pixmap(pix0, mask)
            except:  # fallback to original base image in case of problems
                pix = fitz.Pixmap(doc.extract_image(xref)["image"])

            if pix0.n > 3:
                ext = "pam"
            else:
                ext = "png"

            return {  # create dictionary expected by caller
                "ext": ext,
                "colorspace": pix.colorspace.n,
                "image": pix.tobytes(ext),
            }

        # special case: /ColorSpace definition exists
        # to be sure, we convert these cases to RGB PNG images
        if "/ColorSpace" in doc.xref_object(xref, compressed=True):
            pix = fitz.Pixmap(doc, xref)
            pix = fitz.Pixmap(fitz.csRGB, pix)
            return {  # create dictionary expected by caller
                "ext": "png",
                "colorspace": 3,
                "image": pix.tobytes("png"),
            }
        return doc.extract_image(xref)
    
    def extraerImagenesTextoPDF(self,rutaArchivo):
        textoPdf=""
        t0 = time.time()
        archivoExtension= rutaArchivo.rsplit('.', 1)[1].strip().lower()
        print("\nPara el archivo ",rutaArchivo)
        print("\nInicio de extraer Texto de Imagenes en el ",archivoExtension)
        if (os.path.isfile(rutaArchivo) and archivoExtension=='pdf'):
            for archivo in os.listdir(self.imgDir):
                ruta_imgDir = os.path.join(self.imgDir, archivo)
                os.remove(ruta_imgDir)
            doc = fitz.open(rutaArchivo)
            page_count = doc.page_count  # number of pages
            xreflist = []
            imglist = []
            for pno in range(page_count):
            
                il = doc.get_page_images(pno)
                imglist.extend([x[0] for x in il])
                for img in il:
                    xref = img[0]
                    if xref in xreflist:
                        continue
                    width = img[2]
                    height = img[3]
                    if min(width, height) <= self.dimlimit:
                        continue
                    image = self.recoverpix(doc, img)
                    n = image["colorspace"]
                    imgdata = image["image"]

                    if len(imgdata) <= self.abssize:
                        continue
                    if len(imgdata) / (width * height * n) <= self.relsize:
                        continue
                    try:
                        imgfile = os.path.join(self.imgDir, "img%05i.%s" % (xref, image["ext"]))
                        fout = open(imgfile, "wb")
                        fout.write(imgdata)
                        fout.close()
                    
                        imgLoad = Image.open(imgfile)
                        textoPdf+= pytesseract.image_to_string(imgLoad)
                        print("PAGINA:",il,"/",page_count,"xrefImg:",xref)
                        #print("PAGINA:",il,", xrefImg:",xref,"\nTExto:",textoPdf)
                        xreflist.append(xref)
                    except IOError:
                        print("No es una imagen:",imgfile)

            t1 = time.time()
            imglist = list(set(imglist))
            print(len(set(imglist)), "images in total",len(xreflist), "images extracted","total time %g sec" % (t1 - t0))
        else:
            textoPdf="----SIN TEXTO---"
            
        return textoPdf
