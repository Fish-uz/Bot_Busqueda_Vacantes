import os
import asyncio
from datetime import datetime
from telethon import events
from client_telegram import client
from config import GRUPOS_RELEVANTES, logger
from utils import Log, generar_hash_mensaje
from cerebro import analizar_vacante
from ocr_engine import extraer_texto_de_imagen
from database import existe_hash, guardar_hash

# Carpeta para imágenes temporales
TEMP_DIR = "temp_images"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Almacenamiento volátil para evitar llamadas excesivas a la API de Telegram
cache_nombres_grupos = {}

@client.on(events.NewMessage(chats=GRUPOS_RELEVANTES))
async def manejador_de_vacantes(event):
    """
    Procesa mensajes entrantes, aplica OCR si es necesario, 
    filtra duplicados con DB y analiza con IA.
    """
    chat_id = event.chat_id
    fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # 1. Identificación del Grupo
    if chat_id not in cache_nombres_grupos:
        chat = await event.get_chat()
        cache_nombres_grupos[chat_id] = getattr(chat, 'title', 'Desconocido')
    
    nombre_grupo = cache_nombres_grupos[chat_id]
    Log.info(f"Nuevo mensaje en [{nombre_grupo}]")
    
    texto_final = ""

    # 2. Procesamiento de Contenido (Texto o Imagen)
    if event.photo:
        Log.ocr(f"📸 Detectada imagen. Procesando OCR...")
        nombre_archivo = f"img_{event.message.id}.jpg"
        path = os.path.join(TEMP_DIR, nombre_archivo)
        
        try:
            path = await event.download_media(file=path)
            texto_final = extraer_texto_de_imagen(path)
        except Exception as e:
            Log.error(f"Error descargando imagen: {e}")
        finally:
            if path and os.path.exists(path):
                os.remove(path)
    else:
        texto_final = event.raw_text

    # 3. Validación de Contenido Vacío
    if not texto_final or not texto_final.strip():
        return

    # 4. Registro en Log de OCR/Texto (Para auditoría)
    _registrar_en_archivo(nombre_grupo, fecha_hora, texto_final)

    # 5. Sistema Anti-Spam (Base de Datos)
    hash_msg = generar_hash_mensaje(texto_final)
    if existe_hash(hash_msg):
        Log.alerta(f"Mensaje ignorado: Ya procesado (Anti-Spam).")
        return

    # Guardamos el hash de inmediato para evitar procesamientos paralelos del mismo msj
    guardar_hash(hash_msg)

    # 6. Análisis con IA (Groq/Gemini Fallback)
    await asyncio.sleep(1) # Pausa técnica
    es_relevante = analizar_vacante(texto_final)
    
    if es_relevante:
        Log.exito("¡MATCH! Vacante relevante encontrada. Reenviando...")
        await event.forward_to('me') 
    else:
        Log.alerta("Descartado por la IA.")

def _registrar_en_archivo(grupo, fecha, texto):
    """Maneja la escritura en el archivo de registro histórico."""
    try:
        # Control de peso (100 MB)
        if os.path.exists("log_ocr.txt") and os.path.getsize("log_ocr.txt") > (100 * 1024 * 1024):
            os.remove("log_ocr.txt") 

        separador = "="*60
        with open("log_ocr.txt", "a", encoding="utf-8") as f:
            f.write(f"\n{separador}\n")
            f.write(f"FECHA: {fecha} | GRUPO: {grupo}\n")
            f.write(f"CONTENIDO:\n{texto.strip()}\n")
            f.write(f"{separador}\n")
    except Exception as e:
        Log.error(f"No se pudo escribir en log_ocr.txt: {e}")

async def iniciar_monitor():
    """Mantiene el cliente de Telegram en escucha activa permanente."""
    Log.info("SISTEMA DE VIGILANCIA ACTIVADO. Escuchando...")
    await client.run_until_disconnected()