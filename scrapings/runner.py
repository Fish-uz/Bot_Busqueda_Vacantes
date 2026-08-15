import asyncio

from config import SCRAPING_INTERVAL_MINUTES, logger
from scrapings.scraper_bumeran import ejecutar_scraping_bumeran
from scrapings.scraper_computrabajo import ejecutar_scraping_computrabajo
from scrapings.scraper_gentetop import ejecutar_scraping_gentetop


SCRAPERS = (
    ("Computrabajo", ejecutar_scraping_computrabajo),
    ("Bumeran", ejecutar_scraping_bumeran),
    ("Gente Top", ejecutar_scraping_gentetop),
)


async def ejecutar_scrapings(client):
    resumen = {}
    for nombre, scraper in SCRAPERS:
        try:
            resumen[nombre] = await scraper(client)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Falló el ciclo de %s", nombre)
            resumen[nombre] = {"errores": 1}
    return resumen


async def bucle_scrapings(client):
    intervalo = SCRAPING_INTERVAL_MINUTES * 60
    while True:
        logger.info("Iniciando ciclo de portales de empleo")
        resumen = await ejecutar_scrapings(client)
        logger.info("Ciclo de portales terminado: %s", resumen)
        await asyncio.sleep(intervalo)
