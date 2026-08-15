import os
import platform

import pytesseract
from PIL import Image

from config import TESSERACT_CMD, TESSERACT_LANG, logger


def _configurar_tesseract():
    if TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
    elif platform.system() == "Windows":
        pytesseract.pytesseract.tesseract_cmd = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )
    else:
        pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


def extraer_texto_de_imagen(ruta_imagen):
    if not os.path.exists(ruta_imagen):
        logger.error("Archivo de imagen no encontrado: %s", ruta_imagen)
        return ""
    try:
        _configurar_tesseract()
        with Image.open(ruta_imagen) as imagen:
            try:
                texto = pytesseract.image_to_string(imagen, lang=TESSERACT_LANG)
            except pytesseract.TesseractError:
                logger.warning("No está disponible OCR '%s'; usando idioma por defecto", TESSERACT_LANG)
                texto = pytesseract.image_to_string(imagen)
        return texto.strip()
    except Exception:
        logger.exception("Error en el motor OCR")
        return ""
