import asyncio
from dataclasses import dataclass
from html import unescape
from urllib.parse import urljoin

import requests

from cerebro import EstadoAnalisis, analizar_vacante_detallado
from config import TELEGRAM_DESTINO, logger
from database import marcar_hash, reservar_hash
from utils import generar_hash_mensaje


HEADERS = {
    "User-Agent": "BotVacantes/1.0 (lector de ofertas públicas; contacto local)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "es-VE,es;q=0.9",
}


@dataclass(frozen=True)
class Oferta:
    fuente: str
    area: str
    titulo: str
    url: str
    empresa: str = ""
    descripcion: str = ""

    def texto_analisis(self):
        partes = [
            f"FUENTE: {self.fuente}",
            f"ÁREA: {self.area}",
            f"PUESTO: {self.titulo}",
            f"EMPRESA: {self.empresa or 'No indicada'}",
            f"DETALLE: {self.descripcion or 'Sin descripción breve'}",
            f"ENLACE: {self.url}",
        ]
        return "\n".join(partes)

    def clave(self):
        return generar_hash_mensaje(f"scraping|{self.fuente}|{self.url}")

    def mensaje_telegram(self):
        empresa = f"\n🏢 Empresa: {self.empresa}" if self.empresa else ""
        resumen = f"\n\n📝 {self.descripcion}" if self.descripcion else ""
        return (
            f"🎯 Nueva vacante en {self.fuente}\n\n"
            f"💼 Puesto: {self.titulo}{empresa}\n"
            f"📂 Área: {self.area}\n"
            f"🔗 Postúlate: {self.url}{resumen}"
        )


def texto_limpio(elemento):
    if elemento is None:
        return ""
    return " ".join(unescape(elemento.get_text(" ", strip=True)).split())


def url_absoluta(base, href):
    return urljoin(base, href or "")


def descargar_html(url, timeout=20):
    respuesta = requests.get(url, headers=HEADERS, timeout=timeout)
    respuesta.raise_for_status()
    if "text/html" not in respuesta.headers.get("Content-Type", "text/html"):
        raise ValueError(f"Respuesta no HTML desde {url}")
    contenido_normalizado = respuesta.text.casefold().replace(" ", "")
    if "window.location.href=\"/lander\"" in contenido_normalizado:
        raise RuntimeError(f"{url} exige una navegación JavaScript")
    return respuesta.text


async def procesar_ofertas(ofertas, client):
    estadisticas = {"nuevas": 0, "duplicadas": 0, "aceptadas": 0, "errores": 0}
    for oferta in ofertas:
        clave = oferta.clave()
        if not reservar_hash(clave):
            estadisticas["duplicadas"] += 1
            continue
        estadisticas["nuevas"] += 1
        resultado = await asyncio.to_thread(
            analizar_vacante_detallado, oferta.texto_analisis()
        )
        if resultado.estado is EstadoAnalisis.ERROR:
            marcar_hash(clave, "error")
            estadisticas["errores"] += 1
            logger.error("%s quedó pendiente: %s", oferta.url, resultado.motivo)
            continue
        marcar_hash(clave, "procesado")
        if resultado.aceptada:
            await client.send_message(
                TELEGRAM_DESTINO, oferta.mensaje_telegram(), parse_mode=None
            )
            estadisticas["aceptadas"] += 1
    return estadisticas
