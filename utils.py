import os
import hashlib
from datetime import datetime

# =================================================================
# CONFIGURACIÓN DE ENTORNO
# =================================================================
# Esto asegura que los códigos de escape ANSI (colores) funcionen 
# correctamente en cualquier terminal de Windows.
os.system('') 

# Nombre del archivo físico para la persistencia del Anti-Spam
HASH_FILE = "hashes_procesados.txt"

class Log:
    """
    Clase de utilidad para la gestión de logs visuales en la terminal.
    Utiliza códigos de colores para facilitar la lectura del monitoreo.
    """
    # Códigos de color ANSI
    VERDE = '\033[32m'
    AMARILLO = '\033[33m'
    ROJO = '\033[31m'
    CYAN = '\033[36m'
    RESET = '\033[0m'

    @staticmethod
    def exito(msj):
        """Log para operaciones exitosas o hallazgos positivos."""
        print(f"{Log.VERDE}[ OK ]{Log.RESET} {msj}")

    @staticmethod
    def alerta(msj):
        """Log para advertencias o descartes controlados."""
        print(f"{Log.AMARILLO}[WARN]{Log.RESET} {msj}")

    @staticmethod
    def error(msj):
        """Log para excepciones y errores críticos."""
        print(f"{Log.ROJO}[ERR ]{Log.RESET} {msj}")

    @staticmethod
    def info(msj):
        """Log para información general de flujo y estado."""
        print(f"{Log.CYAN}[INFO]{Log.RESET} {msj}")
    
    # -------------------------------------------------------------
    # GESTIÓN DE HASHING Y ANTI-SPAM
    # -------------------------------------------------------------
    
def generar_hash_mensaje(texto):
    """
    Crea una huella digital única (MD5) basada en el texto normalizado.
    """
    texto_limpio = "".join(texto.lower().split())
    return hashlib.md5(texto_limpio.encode('utf-8')).hexdigest()

def es_mensaje_repetido(texto_hash):
    """
    Verifica si el hash del mensaje ya fue procesado en el mes corriente.
    """
    mes_actual = datetime.now().strftime("%Y-%m")
    
    if not os.path.exists(HASH_FILE):
        with open(HASH_FILE, "w") as f:
            f.write(f"# Mes:{mes_actual}\n")
        return False

    with open(HASH_FILE, "r") as f:
        lineas = f.readlines()

    if lineas and f"# Mes:{mes_actual}" not in lineas[0]:
        with open(HASH_FILE, "w") as f:
            f.write(f"# Mes:{mes_actual}\n")
        return False

    hashes = [linea.strip() for linea in lineas]
    if texto_hash in hashes:
        return True
    
    with open(HASH_FILE, "a") as f:
        f.write(f"{texto_hash}\n")
    return False