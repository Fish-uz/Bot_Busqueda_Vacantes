import os
import requests
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bs4 import BeautifulSoup
import asyncio
from datetime import datetime
from config import logger
from utils import Log, generar_hash_mensaje, es_mensaje_repetido
from cerebro import analizar_vacante
from client_telegram import client

URLS_OBJETIVO = {
    "Tencologia" : "https://ve.computrabajo.com/empleos-de-informatica-y-telecom-en-distrito-capital-en-caracas",
    "Developer" : "https://ve.computrabajo.com/trabajo-de-desarrollador-en-distrito-capital-en-caracas",
    "ADMIN": "https://ve.computrabajo.com/empleos-de-administracion-oficina-en-distrito-capital-en-caracas"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

async def ejecutar_scraping_computrabajo():
    logger.info("\n================================================\nIniciando escaneo automático de Computrabajo Venezuela\n================================================")
    
    if not client.is_connected():
        await client.connect()

    for area, url in URLS_OBJETIVO.items():
        Log.info(f"Escaneando área: {area}...")
        try:
            respuesta = requests.get(url, headers=HEADERS, timeout=15)
            if respuesta.status_code != 200:
                Log.error(f"Error al acceder a Computrabajo ({area}): Status {respuesta.status_code}")
                continue
                
            soup = BeautifulSoup(respuesta.text, 'html.parser')
            
            # Computrabajo envuelve cada oferta en artículos con la clase 'box_offer'
            ofertas = soup.find_all('article', class_='box_offer')
            Log.info(f"Se encontraron {len(ofertas)} ofertas preliminares en {area}.")

            for oferta in ofertas:
                fecha_tag = oferta.find('p', class_='fs13 fc_aux mt5') # Clase donde Computrabajo pone la fecha
                texto_fecha = fecha_tag.text.lower() if fecha_tag else ""
                
                # Si dice "mes" o "meses", descartamos inmediatamente antes de procesar o gastar IA
                if "mes" in texto_fecha:
                    continue

                enlace_tag = oferta.find('a', class_='js-o-link')
                if not enlace_tag:
                    continue
                    
                titulo = enlace_tag.text.strip()
                enlace_completo = f"https://ve.computrabajo.com{enlace_tag['href']}"
                
                # Intentar extraer la descripción corta que viene en la caja
                descripcion_tag = oferta.find('p')
                descripcion_corta = descripcion_tag.text.strip() if descripcion_tag else ""
                
                # Formatear el bloque completo que analizará la IA y guardará el Anti-Spam
                texto_vacante_completo = (
                    f"FUENTE: Computrabajo ({area})\n"
                    f"PUESTO: {titulo}\n"
                    f"ENLACE: {enlace_completo}\n"
                    f"DETALLE: {descripcion_corta}"
                )

                # 1. Pasar por tu sistema Anti-Spam de Hashing
                hash_oferta = generar_hash_mensaje(texto_vacante_completo)
                if es_mensaje_repetido(hash_oferta):
                    # Omitido silenciosamente si ya es viejo o se procesó
                    continue

                Log.info(f"Nueva oferta detectada: {titulo}. Enviando a la IA...")

                # --- CONTROL MANEJO DE RATE LIMIT (ERROR 429) ---
                intentos = 0
                es_relevante = False
                while intentos < 3:
                    try:
                        es_relevante = analizar_vacante(texto_vacante_completo)
                        break  # Si tiene éxito, sale del bucle de reintentos
                    except Exception as e:
                        if "429" in str(e):
                            intentos += 1
                            Log.alerta(f"Rate limit detectado (429). Esperando 10 segundos (Intento {intentos}/3)...")
                            await asyncio.sleep(10)  # Pausa larga para enfriar la API de Groq
                        else:
                            Log.error(f"Error en la IA: {e}")
                            break

                if es_relevante:
                    Log.exito(f"¡Vacante de Computrabajo aprobada por la IA!: {titulo}")
                    mensaje_telegram = (
                        f"🎯 **¡NUEVA VACANTE ENCONTRADA EN COMPUTRABAJO!**\n\n"
                        f"💼 **Puesto:** {titulo}\n"
                        f"📂 **Área:** {area}\n"
                        f"🔗 **Postúlate aquí:** {enlace_completo}\n\n"
                        f"📝 **Resumen inicial:**\n{descripcion_corta}"
                    )
                    # Te la envía directo a tus Mensajes Guardados de Telegram
                    await client.send_message('me', mensaje_telegram)
                else:
                    Log.alerta(f"Oferta '{titulo}' descartada por la IA.")

                await asyncio.sleep(4)

        except Exception as e:
            Log.error(f"Error crítico procesando el área {area}: {e}")