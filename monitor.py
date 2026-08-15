import asyncio
import os
from datetime import datetime
from uuid import uuid4

from telethon import events

from cerebro import EstadoAnalisis, analizar_vacante_detallado
from config import (
    GRUPOS_RELEVANTES,
    OCR_LOG_PATH,
    TELEGRAM_DESTINO,
    TEMP_DIR,
    logger,
)
from database import marcar_hash, reservar_hash
from ocr_engine import extraer_texto_de_imagen
from utils import generar_hash_mensaje


cache_nombres_grupos = {}


async def manejador_de_vacantes(event):
    chat_id = event.chat_id
    try:
        if chat_id not in cache_nombres_grupos:
            chat = await event.get_chat()
            cache_nombres_grupos[chat_id] = getattr(chat, "title", "Desconocido")
        nombre_grupo = cache_nombres_grupos[chat_id]
        texto_final = event.raw_text or ""

        if event.photo:
            TEMP_DIR.mkdir(parents=True, exist_ok=True)
            nombre = f"img_{chat_id}_{event.message.id}_{uuid4().hex}.jpg"
            ruta = TEMP_DIR / nombre
            ruta_descargada = None
            try:
                ruta_descargada = await event.download_media(file=str(ruta))
                texto_ocr = await asyncio.to_thread(
                    extraer_texto_de_imagen, ruta_descargada
                )
                texto_final = "\n".join(
                    parte for parte in (texto_final.strip(), texto_ocr.strip()) if parte
                )
            finally:
                if ruta_descargada:
                    try:
                        os.remove(ruta_descargada)
                    except FileNotFoundError:
                        pass

        if not texto_final.strip():
            return

        hash_msg = generar_hash_mensaje(texto_final)
        if not reservar_hash(hash_msg):
            logger.info("Mensaje duplicado omitido en %s", nombre_grupo)
            return

        resultado = await asyncio.to_thread(analizar_vacante_detallado, texto_final)
        if resultado.estado is EstadoAnalisis.ERROR:
            marcar_hash(hash_msg, "error")
            logger.error("Análisis pendiente de reintento: %s", resultado.motivo)
            return

        marcar_hash(hash_msg, "procesado")
        _registrar_en_archivo(nombre_grupo, texto_final, resultado.estado.value)
        if resultado.aceptada:
            await event.forward_to(TELEGRAM_DESTINO)
            logger.info("Vacante relevante reenviada desde %s", nombre_grupo)
    except Exception:
        logger.exception("Error procesando un mensaje de Telegram")


def _registrar_en_archivo(grupo, texto, estado):
    """Registra solo el resultado y una huella; no almacena el anuncio completo."""
    OCR_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if OCR_LOG_PATH.exists() and OCR_LOG_PATH.stat().st_size > 5 * 1024 * 1024:
        OCR_LOG_PATH.replace(OCR_LOG_PATH.with_suffix(".txt.1"))
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    huella = generar_hash_mensaje(texto)
    with OCR_LOG_PATH.open("a", encoding="utf-8") as archivo:
        archivo.write(f"{fecha} | {grupo} | {estado} | {huella}\n")


async def iniciar_monitor(client):
    client.add_event_handler(
        manejador_de_vacantes, events.NewMessage(chats=GRUPOS_RELEVANTES)
    )
    logger.info("Sistema de vigilancia activado")
    await client.run_until_disconnected()
