import asyncio
from client_telegram import conectar_telegram, client
from monitor import iniciar_monitor
from utils import Log

# =================================================================
# FUNCIÓN DE ARRANQUE PRINCIPAL
# =================================================================
async def main():
    """
    Coordina la inicialización de la aplicación, estableciendo la 
    conexión con Telegram y activando el bucle de monitoreo.
    """
    Log.info("--- APP DE VACANTES INICIADA ---")
    
    # 1. Establecer conexión inicial con el cliente de Telegram
    await conectar_telegram()
    
    # 2. Iniciar el servicio de escucha activa en los grupos definidos
    # Este proceso se mantiene en ejecución hasta que sea interrumpido
    await iniciar_monitor()

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