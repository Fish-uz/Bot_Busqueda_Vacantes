import os
import asyncio
import logging
from datetime import datetime
import pytesseract
from PIL import Image
from telethon import events
from client_telegram import client
from config import GRUPOS_RELEVANTES, logger
from utils import Log, generar_hash_mensaje, es_mensaje_repetido
from cerebro import analizar_vacante

# =================================================================
# CONFIGURACIÓN DE LOGS ESPECÍFICOS PARA EL MONITOR
# =================================================================

# Configuración de la ruta del ejecutable de Tesseract (Motor OCR)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Almacenamiento volátil para evitar llamadas excesivas a la API de Telegram por metadatos
cache_nombres_grupos = {}

# =================================================================
# MANEJADOR DE EVENTOS DE NUEVOS MENSAJES
# =================================================================
@client.on(events.NewMessage(chats=GRUPOS_RELEVANTES))
async def manejador_de_vacantes(event):
    """
    Función principal que procesa cada mensaje entrante de los grupos monitoreados.
    Gestiona la extracción de texto (OCR si es imagen), el filtrado anti-spam y la IA.
    """
    chat_id = event.chat_id
    fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Identificación del nombre del grupo (Uso de caché para optimizar rendimiento)
    if chat_id not in cache_nombres_grupos:
        chat = await event.get_chat()
        nombre = getattr(chat, 'title', 'Desconocido')
        cache_nombres_grupos[chat_id] = nombre
    
    nombre_grupo = cache_nombres_grupos[chat_id]

    # --- TUS LOGS ORIGINALES ---
    Log.info(f"Mensaje recibido de: {nombre_grupo} (ID: {chat_id}) ({fecha_hora})")
    
    texto_final = ""

    # -------------------------------------------------------------
    # PROCESAMIENTO DE CONTENIDO MULTIMEDIA (OCR)
    # -------------------------------------------------------------
    if event.photo:
        Log.info(f"📸 Imagen detectada en {nombre_grupo}. Extrayendo texto...")
        path = await event.download_media() # Descarga temporal de la imagen
        try:
            # Conversión de imagen a texto mediante OCR local
            texto_final = pytesseract.image_to_string(Image.open(path))
        except Exception as e:
            Log.error(f"Error al leer imagen: {e}")
        finally:
            # Garantiza la eliminación del archivo para evitar consumo de disco
            if os.path.exists(path):
                os.remove(path)
                Log.info(f"Archivo temporal {path} eliminado.")
    else:
        # Extracción directa de texto si no es un archivo de imagen
        texto_final = event.raw_text

    Log.info(f"[ OK ] Contenido capturado en {nombre_grupo} ({chat_id})")

    # -------------------------------------------------------------
    # LÓGICA DE FILTRADO Y ANÁLISIS
    # -------------------------------------------------------------
    if texto_final.strip():
        # 1. Sistema Anti-Spam basado en Hashing (Persistencia Mensual)
        hash_msg = generar_hash_mensaje(texto_final)
        if es_mensaje_repetido(hash_msg):
            Log.alerta(f"Mensaje omitido: Ya fue procesado anteriormente (Anti-Spam).")
            return # Finaliza el proceso para este mensaje

        # Pequeña pausa de cortesía para el flujo asíncrono
        await asyncio.sleep(2)

        # 2. Análisis Semántico mediante el Cerebro (IA Groq)
        es_relevante = analizar_vacante(texto_final)
        
        # 3. Acción de Reenvío
        if es_relevante:
            Log.exito("¡ESTA VACANTE ES PARA TI! Reenviando...")
            # Reenvía el mensaje original a "Mensajes Guardados" (me)
            await event.forward_to('me') 
        else:
            Log.alerta("Mensaje descartado por la IA (No relevante).")

# =================================================================
# INICIO DEL SERVICIO DE MONITOREO
# =================================================================
async def iniciar_monitor():
    """Mantiene el cliente de Telegram en escucha activa permanente."""
    Log.info("Iniciando modo vigilancia. Presiona Ctrl+C para detener.")
    await client.run_until_disconnected()