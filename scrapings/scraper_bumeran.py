import os
import sys
import requests
from bs4 import BeautifulSoup
import asyncio

# Permitir buscar módulos en la carpeta raíz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import Log, generar_hash_mensaje, es_mensaje_repetido
from cerebro import analizar_vacante
from client_telegram import client

# URLs web públicas de Bumeran Venezuela (Filtro: Caracas)
URLS_BUMERAN = {
    "Tecnologia": "https://www.bumeran.com.ve/empleos-busqueda-caracas-tecnologia-sistemas.html",
    "ADMIN": "https://www.bumeran.com.ve/empleos-busqueda-caracas-administracion-contabilidad.html"
}

# Cabeceras hiperrealistas para evadir la detección de bots básicos
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

async def ejecutar_scraping_bumeran():
    Log.info("\n================================================\nIniciando escaneo automático de Bumeran Venezuela\n================================================")
    
    if not client.is_connected():
        await client.connect()

    for area, url in URLS_BUMERAN.items():
        Log.info(f"Escaneando Bumeran en el área: {area}...")
        try:
            # Usamos una sesión para mantener persistencia si es necesario
            sesion = requests.Session()
            respuesta = sesion.get(url, headers=HEADERS, timeout=15)
            
            if respuesta.status_code != 200:
                Log.error(f"Error al acceder a Bumeran ({area}): Status {respuesta.status_code}")
                continue
            
            soup = BeautifulSoup(respuesta.text, 'html.parser')
            
            # Selector actualizado: Bumeran envuelve sus ofertas principales en elementos "div" con propiedad "component" o clases "sc-"
            # Buscaremos todos los enlaces que apunten a un aviso de empleo directo
            enlaces_ofertas = soup.find_all('a', href=lambda h: h and "/empleos/aviso-" in h)
            
            # Eliminar duplicados de enlaces en la misma página
            enlaces_unicos = list(set([e['href'] for e in enlaces_ofertas]))
            Log.info(f"Se encontraron {len(enlaces_unicos)} ofertas potenciales en Bumeran ({area}).")

            for href in enlaces_unicos:
                enlace_completo = f"https://www.bumeran.com.ve{href}"
                
                # Para la lista, generamos un título limpio basado en la URL del enlace
                # Las URLs de bumeran tienen la estructura: /empleos/puesto-de-trabajo-aviso-123.html
                parte_titulo = href.split('/')[-1].replace('.html', '').split('-aviso-')[0]
                titulo = parte_titulo.replace('-', ' ').capitalize()

                texto_vacante_completo = (
                    f"FUENTE: Bumeran ({area})\n"
                    f"PUESTO: {titulo}\n"
                    f"ENLACE: {enlace_completo}\n"
                    f"DETALLE: Revisar perfil completo en el enlace adjunto."
                )

                # 1. Filtro Anti-Spam
                hash_oferta = generar_hash_mensaje(texto_vacante_completo)
                if es_mensaje_repetido(hash_oferta):
                    continue

                Log.info(f"Nueva oferta en Bumeran: '{titulo}'. Enviando a la IA...")

                # 2. Manejo de Rate Limit (429) de Groq
                intentos = 0
                es_relevante = False
                while intentos < 3:
                    try:
                        es_relevante = analizar_vacante(texto_vacante_completo)
                        break
                    except Exception as e:
                        if "429" in str(e):
                            intentos += 1
                            Log.alerta(f"Rate limit detectado (429). Esperando 10 segundos (Intento {intentos}/3)...")
                            await asyncio.sleep(10)
                        else:
                            Log.error(f"Error en la IA al procesar Bumeran: {e}")
                            break

                # 3. Envío si califica
                if es_relevante:
                    Log.exito(f"¡Vacante de Bumeran aprobada por la IA!: {titulo}")
                    mensaje_telegram = (
                        f"🎯 **¡NUEVA VACANTE ENCONTRADA EN BUMERAN!**\n\n"
                        f"💼 **Puesto:** {titulo}\n"
                        f"📂 **Área:** {area}\n"
                        f"🔗 **Postúlate aquí:** {enlace_completo}"
                    )
                    await client.send_message('me', mensaje_telegram)
                else:
                    Log.alerta(f"Oferta '{titulo}' descartada por la IA.")

                await asyncio.sleep(4)

        except Exception as e:
            Log.error(f"Error crítico procesando Bumeran en el área {area}: {e}")