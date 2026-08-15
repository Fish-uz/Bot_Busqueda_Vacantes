import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _configurar_logging():
    logger_configurado = logging.getLogger("BotVacantes")
    if logger_configurado.handlers:
        return logger_configurado
    logger_configurado.setLevel(logging.INFO)
    formato = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    archivo = RotatingFileHandler(
        BASE_DIR / "bot_vigilancia.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    consola = logging.StreamHandler()
    archivo.setFormatter(formato)
    consola.setFormatter(formato)
    logger_configurado.addHandler(archivo)
    logger_configurado.addHandler(consola)
    logger_configurado.propagate = False
    return logger_configurado


logger = _configurar_logging()


def _leer_entero(nombre):
    valor = os.getenv(nombre, "").strip()
    if not valor:
        return None
    try:
        return int(valor)
    except ValueError:
        return None


def _leer_grupos(valor):
    grupos = []
    invalidos = []
    for elemento in valor.split(","):
        elemento = elemento.strip()
        if not elemento:
            continue
        try:
            grupos.append(int(elemento))
        except ValueError:
            invalidos.append(elemento)
    return grupos, invalidos


API_ID = _leer_entero("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH", "").strip()
GROQ_KEY = os.getenv("GROQ_API_KEY", "").strip()
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash").strip()
GRUPOS_RELEVANTES, GRUPOS_INVALIDOS = _leer_grupos(
    os.getenv("TELEGRAM_GRUPOS_VACANTES", "")
)

DB_PATH = Path(os.getenv("VACANTES_DB_PATH", BASE_DIR / "vacantes_data.db"))
OCR_LOG_PATH = Path(os.getenv("OCR_LOG_PATH", BASE_DIR / "log_ocr.txt"))
TEMP_DIR = Path(os.getenv("TEMP_IMAGES_DIR", BASE_DIR / "temp_images"))
TELEGRAM_SESSION = os.getenv("TELEGRAM_SESSION", str(BASE_DIR / "sesion_frank"))
TELEGRAM_DESTINO = os.getenv("TELEGRAM_DESTINO", "me")
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "").strip()
TESSERACT_LANG = os.getenv("TESSERACT_LANG", "spa").strip() or "spa"


def validar_configuracion(requerir_ia=True):
    """Devuelve una lista de errores de configuración legibles."""
    errores = []
    if API_ID is None:
        errores.append("TELEGRAM_API_ID falta o no es un número entero")
    if not API_HASH:
        errores.append("falta TELEGRAM_API_HASH")
    if not GRUPOS_RELEVANTES:
        errores.append("TELEGRAM_GRUPOS_VACANTES no contiene grupos válidos")
    if GRUPOS_INVALIDOS:
        errores.append("IDs de grupos inválidos: " + ", ".join(GRUPOS_INVALIDOS))
    if requerir_ia and not (GROQ_KEY or GEMINI_KEY):
        errores.append("se requiere GROQ_API_KEY o GEMINI_API_KEY")
    return errores


logger.info("Configuración cargada: %d grupos válidos.", len(GRUPOS_RELEVANTES))
