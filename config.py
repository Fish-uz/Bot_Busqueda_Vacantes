import os
import logging
from utils import Log
from dotenv import load_dotenv

# =================================================================
# 1. CARGA DE VARIABLES DE ENTORNO
# =================================================================
# Se cargan las credenciales y configuraciones desde el archivo .env
load_dotenv()

# =================================================================
# 2. CONFIGURACIÓN DEL SISTEMA DE LOGS
# =================================================================
# Se establece un sistema de registro dual: 
# - Archivo (bot_vacantes.log) para persistencia.
# - Consola (StreamHandler) para monitoreo en tiempo real.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_vigilancia.log"), # Registro persistente
        logging.StreamHandler()                # Visualización en terminal
    ]
)

# Instancia global del logger para ser usada en otros módulos
logger = logging.getLogger("BotVacantes")

# =================================================================
# 3. DEFINICIÓN DE VARIABLES GLOBALES Y CREDENCIALES
# =================================================================
# Credenciales de la API de Telegram y la API Key de Groq
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
GROQ_KEY = os.getenv("GROQ_API_KEY")

logger.info("Configuración cargada exitosamente.")

# -----------------------------------------------------------------
# PROCESAMIENTO DE IDs DE GRUPOS
# -----------------------------------------------------------------
# Se recupera la cadena de IDs desde el .env (ejemplo: "123,456,789")
ids_raw = os.getenv("TELEGRAM_GRUPOS_VACANTES", "")

# Limpieza y conversión:
# 1. Se separa por comas.
# 2. Se eliminan espacios en blanco.
# 3. Se convierten los valores a enteros (int) para compatibilidad con Telethon.
GRUPOS_RELEVANTES = [int(i.strip()) for i in ids_raw.split(",") if i.strip()]

logger.info(f"Grupos monitoreados: {len(GRUPOS_RELEVANTES)} IDs cargados.")