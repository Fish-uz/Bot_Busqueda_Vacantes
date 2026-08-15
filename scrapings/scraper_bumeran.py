import asyncio
import re

from bs4 import BeautifulSoup

from config import logger
from scrapings.base import Oferta, descargar_html, procesar_ofertas, texto_limpio, url_absoluta


BASE_URL = "https://www.bumeran.com.ve"
URLS_BUMERAN = {
    "Tecnología": f"{BASE_URL}/empleos-busqueda-caracas-tecnologia-sistemas.html",
    "Administración": f"{BASE_URL}/empleos-busqueda-caracas-administracion-contabilidad.html",
}


def _titulo_desde_url(url):
    slug = url.rstrip("/").split("/")[-1].removesuffix(".html")
    slug = re.sub(r"-aviso-.*$", "", slug)
    return slug.replace("-", " ").strip().title()


def extraer_ofertas(html, area):
    soup = BeautifulSoup(html, "html.parser")
    enlaces = soup.select("a[href*='/empleos/']")
    ofertas = []
    vistas = set()
    for enlace in enlaces:
        href = enlace.get("href", "")
        if "aviso" not in href and not re.search(r"-\d+\.html(?:$|\?)", href):
            continue
        url = url_absoluta(BASE_URL, href)
        if url in vistas:
            continue
        vistas.add(url)
        titulo = texto_limpio(enlace) or _titulo_desde_url(url)
        contenedor = enlace.find_parent("article") or enlace.find_parent("div")
        descripcion = texto_limpio(contenedor)[:600]
        if titulo:
            ofertas.append(Oferta("Bumeran", area, titulo, url, descripcion=descripcion))
    return ofertas


async def obtener_ofertas(fetch=descargar_html):
    ofertas = []
    for area, url in URLS_BUMERAN.items():
        try:
            html = await asyncio.to_thread(fetch, url)
            encontradas = extraer_ofertas(html, area)
            logger.info("Bumeran %s: %d ofertas", area, len(encontradas))
            ofertas.extend(encontradas)
        except Exception:
            logger.exception("No se pudo consultar Bumeran (%s)", area)
    return ofertas


async def ejecutar_scraping_bumeran(client, fetch=descargar_html):
    return await procesar_ofertas(await obtener_ofertas(fetch), client)
