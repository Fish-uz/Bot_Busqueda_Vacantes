import asyncio

from bs4 import BeautifulSoup

from config import logger
from scrapings.base import Oferta, descargar_html, procesar_ofertas, texto_limpio, url_absoluta


BASE_URL = "https://www.gentetop.com"
URLS_GENTETOP = {
    "Tecnología": f"{BASE_URL}/ve/buscar-empleo-de-informatica-sistemas-en-distrito-capital",
    "Administración": f"{BASE_URL}/ve/buscar-empleo-de-administracion-oficina-en-distrito-capital",
}


def extraer_ofertas(html, area):
    soup = BeautifulSoup(html, "html.parser")
    enlaces = soup.select("a[href*='/ve/empleo/']")
    ofertas = []
    vistas = set()
    for enlace in enlaces:
        url = url_absoluta(BASE_URL, enlace.get("href"))
        if not url or url in vistas:
            continue
        vistas.add(url)
        titulo = texto_limpio(enlace)
        if len(titulo) < 5:
            continue
        contenedor = enlace.find_parent("article") or enlace.find_parent("div")
        descripcion = texto_limpio(contenedor)[:600]
        empresa = ""
        if contenedor:
            candidato = contenedor.select_one("[class*='company'], [class*='empresa']")
            empresa = texto_limpio(candidato)
        ofertas.append(Oferta("Gente Top", area, titulo, url, empresa, descripcion))
    return ofertas


async def obtener_ofertas(fetch=descargar_html):
    ofertas = []
    for area, url in URLS_GENTETOP.items():
        try:
            html = await asyncio.to_thread(fetch, url)
            encontradas = extraer_ofertas(html, area)
            logger.info("Gente Top %s: %d ofertas", area, len(encontradas))
            ofertas.extend(encontradas)
        except Exception:
            logger.exception("No se pudo consultar Gente Top (%s)", area)
    return ofertas


async def ejecutar_scraping_gentetop(client, fetch=descargar_html):
    return await procesar_ofertas(await obtener_ofertas(fetch), client)
