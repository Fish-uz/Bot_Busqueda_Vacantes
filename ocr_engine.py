import pytesseract
from PIL import Image
import platform
import os
from utils import Log

# --- CONFIGURACIÓN DE TESSERACT ---
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
else:
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

def extraer_texto_de_imagen(ruta_imagen):
    """
    Intenta extraer texto de una imagen usando Tesseract.
    Maneja errores de forma elegante para no interrumpir el flujo del bot.
    """
    if not os.path.exists(ruta_imagen):
        Log.error(f"Archivo de imagen no encontrado: {ruta_imagen}")
        return ""

    try:
        Log.info(f"Procesando OCR para: {os.path.basename(ruta_imagen)}...")
        # Abrimos la imagen y aplicamos OCR
        with Image.open(ruta_imagen) as img:
            texto = pytesseract.image_to_string(img)
        
        return texto.strip()
    except Exception as e:
        Log.error(f"Error crítico en motor OCR: {e}")
        return ""
