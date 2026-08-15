import asyncio

from bs4 import BeautifulSoup

from config import logger
from scrapings.base import Oferta, descargar_html, procesar_ofertas, texto_limpio, url_absoluta


BASE_URL = "https://ve.computrabajo.com"
URLS_OBJETIVO = {
    "Tecnología": f"{BASE_URL}/empleos-de-informatica-y-telecom-en-distrito-capital-en-caracas",
    "Desarrollo": f"{BASE_URL}/trabajo-de-desarrollador-en-distrito-capital-en-caracas",
    "Administración": f"{BASE_URL}/empleos-de-administracion-oficina-en-distrito-capital-en-caracas",
}


def extraer_ofertas(html, area):
    soup = BeautifulSoup(html, "html.parser")
    selectores = (
        "article.box_offer a.js-o-link[href]",
        "article a[href*='/ofertas-de-trabajo/oferta-de-trabajo']",
        "a[href*='/ofertas-de-trabajo/oferta-de-trabajo']",
    )
    enlaces = []
    for selector in selectores:
        enlaces = soup.select(selector)
        if enlaces:
            break

    ofertas = []
    vistas = set()
    for enlace in enlaces:
        url = url_absoluta(BASE_URL, enlace.get("href"))
        if not url or url in vistas:
            continue
        vistas.add(url)
        titulo = texto_limpio(enlace)
        contenedor = enlace.find_parent("article") or enlace.find_parent("div")
        bloque = texto_limpio(contenedor)
        if not titulo or "más de 30 días" in bloque.casefold():
            continue
        descripcion = bloque[:600] if bloque != titulo else ""
        ofertas.append(
            Oferta("Computrabajo", area, titulo, url, descripcion=descripcion)
        )
    return ofertas


async def obtener_ofertas(fetch=descargar_html):
    ofertas = []
    for area, url in URLS_OBJETIVO.items():
        try:
            html = await asyncio.to_thread(fetch, url)
            encontradas = extraer_ofertas(html, area)
            logger.info("Computrabajo %s: %d ofertas", area, len(encontradas))
            ofertas.extend(encontradas)
        except Exception:
            logger.exception("No se pudo consultar Computrabajo (%s)", area)
    return ofertas


async def ejecutar_scraping_computrabajo(client, fetch=descargar_html):
    return await procesar_ofertas(await obtener_ofertas(fetch), client)
