from telethon import TelegramClient
from utils import Log
from config import API_ID, API_HASH, logger

# =================================================================
# INICIALIZACIÓN DEL CLIENTE
# =================================================================
# Se crea la instancia de TelegramClient usando el archivo de sesión local
# y las credenciales obtenidas desde el archivo de configuración.
client = TelegramClient('sesion_frank', API_ID, API_HASH)

async def conectar_telegram():
    """
    Gestiona el proceso de autenticación y conexión con los servidores de Telegram.
    Verifica si la sesión actual es válida y cuenta con autorización.
    """
    logger.info("Intentando conectar a Telegram...")
    try:
        # Inicia el cliente (solicitará datos por consola si la sesión no existe)
        await client.start()
        
        # Validación de estado de autorización del usuario
        if await client.is_user_authorized():
            logger.info("Conexión establecida y usuario autorizado.")
        else:
            logger.warning("Usuario no autorizado. Se requiere intervención manual.")
    except Exception as e:
        # Registro de errores críticos durante el handshake inicial
        logger.error(f"Error fatal al conectar a Telegram: {e}", exc_info=True)

async def obtener_grupos():
    """
    Itera sobre los diálogos activos del usuario para extraer una lista
    de grupos y canales disponibles.
    """
    logger.info("Iniciando escaneo de grupos y canales...")
    grupos_interes = []
    try:
        # Itera de forma asíncrona sobre todos los diálogos abiertos
        async for dialog in client.iter_dialogs():
            # Filtramos únicamente entidades colectivas (Grupos y Canales)
            if dialog.is_group or dialog.is_channel:
                logger.debug(f"Encontrado: {dialog.name} (ID: {dialog.id})")
                grupos_interes.append({"name": dialog.name, "id": dialog.id})
        
        logger.info(f"Escaneo finalizado. Se encontraron {len(grupos_interes)} grupos/canales.")
        return grupos_interes
    except Exception as e:
        # Manejo de excepciones durante la iteración de diálogos
        logger.error(f"Error al obtener la lista de grupos: {e}")
        return []

async def main():
    """
    Función principal encargada de coordinar la conexión y la
    visualización de los metadatos de los grupos.
    """
    # 1. Ejecución del proceso de conexión
    await conectar_telegram()
    
    # 2. Extracción de metadatos de grupos y canales
    grupos = await obtener_grupos()
    
    # 3. Presentación formateada de resultados en la terminal
    print("\n" + "="*50)
    print("LISTADO DE TUS GRUPOS Y CANALES:")
    print("="*50)
    for g in grupos:
        print(f"NOMBRE: {g['name']} | ID: {g['id']}")
    print("="*50 + "\n")

# =================================================================
# PUNTO DE ENTRADA DEL SCRIPT
# =================================================================
# Disparador para la ejecución del bucle de eventos asíncrono
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())