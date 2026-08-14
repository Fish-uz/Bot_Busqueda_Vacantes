import os
import hashlib
from datetime import datetime

# =================================================================
# CONFIGURACIÓN DE ENTORNO
# =================================================================
os.system('') 

class Log:
    """
    Clase de utilidad para la gestión de logs visuales en la terminal.
    Utiliza códigos de colores para facilitar la lectura del monitoreo.
    """
    VERDE = '\033[32m'
    AMARILLO = '\033[33m'
    ROJO = '\033[31m'
    CYAN = '\033[36m'
    MAGENTA = '\033[35m'
    RESET = '\033[0m'

    @staticmethod
    def exito(msj):
        print(f"{Log.VERDE}[ OK ]{Log.RESET} {msj}")

    @staticmethod
    def alerta(msj):
        print(f"{Log.AMARILLO}[WARN]{Log.RESET} {msj}")

    @staticmethod
    def error(msj):
        print(f"{Log.ROJO}[ERR ]{Log.RESET} {msj}")

    @staticmethod
    def info(msj):
        print(f"{Log.CYAN}[INFO]{Log.RESET} {msj}")

    @staticmethod
    def ocr(msj):
        print(f"{Log.MAGENTA}[OCR ]{Log.RESET} {msj}")
    
def generar_hash_mensaje(texto):
    """
    Crea una huella digital única (MD5) basada en el texto normalizado.
    Se eliminan espacios, saltos de línea y se pasa a minúsculas.
    """
    texto_limpio = "".join(texto.lower().split())
    return hashlib.md5(texto_limpio.encode('utf-8')).hexdigest()
