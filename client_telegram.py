import asyncio

from telethon import TelegramClient

from config import API_HASH, API_ID, TELEGRAM_SESSION, logger, validar_configuracion


_client = None


def obtener_cliente():
    """Construye el cliente solo después de validar su configuración."""
    global _client
    if _client is None:
        errores = validar_configuracion(requerir_ia=False)
        if errores:
            raise RuntimeError("Configuración inválida: " + "; ".join(errores))
        _client = TelegramClient(TELEGRAM_SESSION, API_ID, API_HASH)
    return _client


async def conectar_telegram():
    cliente = obtener_cliente()
    logger.info("Intentando conectar a Telegram...")
    try:
        await cliente.start()
        if not await cliente.is_user_authorized():
            raise RuntimeError("Telegram requiere autorización manual")
    except Exception:
        logger.exception("No fue posible conectar a Telegram")
        raise
    logger.info("Conexión establecida y usuario autorizado.")
    return cliente


async def obtener_grupos(cliente=None):
    cliente = cliente or obtener_cliente()
    grupos = []
    async for dialog in cliente.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            grupos.append({"name": dialog.name, "id": dialog.id})
    return grupos


async def main():
    cliente = await conectar_telegram()
    grupos = await obtener_grupos(cliente)
    for grupo in grupos:
        print(f"NOMBRE: {grupo['name']} | ID: {grupo['id']}")


if __name__ == "__main__":
    asyncio.run(main())
