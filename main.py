import asyncio
from contextlib import suppress
from client_telegram import conectar_telegram
from monitor import iniciar_monitor
from database import inicializar_db
from config import SCRAPING_ENABLED, logger, validar_configuracion
from scrapings.runner import bucle_scrapings

# =================================================================
# FUNCIÓN DE ARRANQUE PRINCIPAL
# =================================================================
async def main():
    """
    Coordina la inicialización de la aplicación, estableciendo la 
    conexión con Telegram y activando el bucle de monitoreo.
    """
    logger.info("--- INICIANDO SISTEMA DE VACANTES ---")

    errores = validar_configuracion()
    if errores:
        raise RuntimeError("Configuración inválida: " + "; ".join(errores))
    
    inicializar_db()
    client = await conectar_telegram()
    tarea_scrapings = None
    try:
        if SCRAPING_ENABLED:
            tarea_scrapings = asyncio.create_task(
                bucle_scrapings(client), name="scrapings"
            )
        await iniciar_monitor(client)
    finally:
        if tarea_scrapings:
            tarea_scrapings.cancel()
            with suppress(asyncio.CancelledError):
                await tarea_scrapings
        if client.is_connected():
            await client.disconnect()

# =================================================================
# PUNTO DE ENTRADA DEL SISTEMA
# =================================================================
if __name__ == "__main__":
    try:
        # Ejecuta el bucle de eventos asíncrono
        asyncio.run(main())
    except KeyboardInterrupt:
        # Manejo controlado de la salida (Ctrl+C)
        logger.warning("Bot apagado manualmente.")
