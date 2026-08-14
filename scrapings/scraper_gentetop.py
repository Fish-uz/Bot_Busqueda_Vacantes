import os
import sys
import requests
from bs4 import BeautifulSoup
import asyncio

# Permitir buscar módulos en la carpeta raíz tanto en ejecución individual como desde main.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import Log, generar_hash_mensaje, es_mensaje_repetido
from cerebro import analizar_vacante
from client_telegram import client

# URLs públicas de Gente Top filtradas para Caracas (Distrito Capital)
URLS_GENTETOP = {
    "Tecnologia": "https://www.gentetop.com/ve/buscar-empleo-de-informatica-sistemas-en-distrito-capital",
    "ADMIN": "https://www.gentetop.com/ve/buscar-empleo-de-administracion-oficina-en-distrito-capital"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

async def ejecutar_scraping_gentetop():
    Log.info("Iniciando escaneo automático de Gente Top (Empleate)...")
    
    # Verificación de conexión segura para Telegram
    if not client.is_connected():
        await client.connect()

    for area, url in URLS_GENTETOP.items():
        Log.info(f"Escaneando Gente Top en el área: {area}...")
        try:
            respuesta = requests.get(url, headers=HEADERS, timeout=15)
            if respuesta.status_code != 200:
                Log.error(f"Error al acceder a Gente Top ({area}): Status {respuesta.status_code}")
                continue
            
            soup = BeautifulSoup(respuesta.text, 'html.parser')
            
            # CORRECCIÓN DE SELECTOR: Buscamos todas las etiquetas de artículo o divs contenedores de ofertas
            # En Gente Top las ofertas se identifican de forma segura por sus enlaces que contienen '/ve/empleo/'
            enlaces_empleos = soup.find_all('a', href=lambda h: h and "/ve/empleo/" in h)
            
            # Filtramos duplicados manteniendo el orden
            urls_vistas = set()
            ofertas_filtradas = []
            for enc in enlaces_empleos:
                href = enc['href']
                if href not in urls_vistas:
                    urls_vistas.add(href)
                    ofertas_filtradas.append(enc)

            Log.info(f"Se encontraron {len(ofertas_filtradas)} ofertas preliminares en Gente Top ({area}).")

            for oferta in ofertas_filtradas:
                enlace_completo = oferta['href']
                if not enlace_completo.startswith('http'):
                    enlace_completo = f"https://www.gentetop.com{enlace_completo}"
                
                # Intentamos extraer el título directamente del texto del enlace o de su contenedor superior
                titulo = oferta.text.strip()
                if not titulo or len(titulo) < 5:
                    continue

                # Buscamos textos descriptivos cercanos dentro del bloque contenedor del enlace
                contenedor = oferta.find_parent('div')
                descripcion_corta = "Sin descripción corta disponible."
                empresa = "Empresa Confidencial"
                
                if contenedor:
                    p_tag = contenedor.find('p')
                    if p_tag:
                        descripcion_corta = p_tag.text.strip()
                    
                    # Intentar buscar la empresa en etiquetas span o divs pequeños
                    span_tags = contenedor.find_all('span')
                    for span in span_tags:
                        if span.text and len(span.text) < 40 and "publicado" not in span.text.lower():
                            empresa = span.text.strip()
                            break

                texto_vacante_completo = (
                    f"FUENTE: Gente Top ({area})\n"
                    f"EMPRESA: {empresa}\n"
                    f"PUESTO: {titulo}\n"
                    f"ENLACE: {enlace_completo}\n"
                    f"DETALLE: {descripcion_corta}"
                )

                # 1. Filtro Anti-Spam
                hash_oferta = generar_hash_mensaje(texto_vacante_completo)
                if es_mensaje_repetido(hash_oferta):
                    continue

                Log.info(f"Nueva oferta en Gente Top: '{titulo}'. Enviando a la IA...")

                # 2. Control de Rate Limit (429) de Groq
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
                            Log.error(f"Error en la IA al procesar Gente Top: {e}")
                            break

                # 3. Envío si aprueba tu prompt
                if es_relevante:
                    Log.exito(f"¡Vacante aprobada por la IA!: {titulo}")
                    mensaje_telegram = (
                        f"🎯 **¡NUEVA VACANTE ENCONTRADA EN GENTE TOP!**\n\n"
                        f"💼 **Puesto:** {titulo}\n"
                        f"🏢 **Empresa:** {empresa}\n"
                        f"📂 **Área:** {area}\n"
                        f"🔗 **Postúlate aquí:** {enlace_completo}\n\n"
                        f"📝 **Resumen inicial:**\n{descripcion_corta}"
                    )
                    await client.send_message('me', mensaje_telegram)
                else:
                    Log.alerta(f"Oferta '{titulo}' descartada por la IA.")

                await asyncio.sleep(4)

        except Exception as e:
            Log.error(f"Error crítico procesando Gente Top en el área {area}: {e}")

# =================================================================
# BLOQUE DE EJECUCIÓN INDIVIDUAL PARA PRUEBAS
# =================================================================
if __name__ == "__main__":
    from client_telegram import conectar_telegram
    
    async def prueba_local():
        Log.info("--- MODO PRUEBA LOCAL INDIVIDUAL (GENTE TOP) ---")
        await conectar_telegram()
        await ejecutar_scraping_gentetop()
        Log.info("--- FIN DE LA PRUEBA LOCAL ---")
        
    try:
        asyncio.run(prueba_local())
    except KeyboardInterrupt:
        Log.alerta("Prueba cancelada por el usuario.")