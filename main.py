import asyncio
import sys
import os
from client_telegram import conectar_telegram, client
from monitor import iniciar_monitor
from utils import Log
from scrapings.scraper_computrabajo import ejecutar_scraping_computrabajo
from scrapings.scraper_bumeran import ejecutar_scraping_bumeran
from scrapings.scraper_gentetop import ejecutar_scraping_gentetop


# =================================================================
# FUNCIÓN DE ARRANQUE PRINCIPAL
# =================================================================
async def tarea_programada_scrapers():
    """
    Bucle encargado los scrapers webs cada 6 horas, indefinidamente
    """
    segundos_6hrs = 6 * 60 * 60

    await asyncio.sleep(5)

    while True: 
        try:
            await ejecutar_scraping_computrabajo()
            await ejecutar_scraping_gentetop()
            # await ejecutar_scraping_bumeran()

            Log.info("Todos los scrapers web completados. Próxima ronda en 6 horas...")
        except Exception as e:
            Log.error(f"Error en el ciclo de ejecución de scrapers: {e}")
        await asyncio.sleep(segundos_6hrs)

async def main():
    Log.info("--- APP DE VACANTES INICIADA ---")
    
    # 1. Establecer conexión inicial con el cliente de Telegram
    await conectar_telegram()
    
    await asyncio.gather(
        iniciar_monitor(),
        tarea_programada_scrapers()
    )

# =================================================================
# PUNTO DE ENTRADA DEL SISTEMA
# =================================================================
if __name__ == "__main__":
    try:
        # Ejecuta el bucle de eventos asíncrono
        asyncio.run(main())
    except KeyboardInterrupt:
        # Manejo controlado de la salida (Ctrl+C)
        Log.alerta("Bot apagado manualmente.")