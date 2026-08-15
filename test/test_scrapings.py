import asyncio
from unittest.mock import Mock

import pytest
from cerebro import EstadoAnalisis, ResultadoAnalisis
from scrapings import base
from scrapings.scraper_bumeran import extraer_ofertas as extraer_bumeran
from scrapings.scraper_computrabajo import extraer_ofertas as extraer_computrabajo
from scrapings.scraper_gentetop import extraer_ofertas as extraer_gentetop


def test_extraer_computrabajo_elimina_duplicados_y_antiguas():
    html = """
    <article class="box_offer">
      <a class="js-o-link" href="/ofertas-de-trabajo/oferta-de-trabajo-python-ABC">Developer Python</a>
      <p>Caracas - Hace 2 días</p>
    </article>
    <article><a href="/ofertas-de-trabajo/oferta-de-trabajo-python-ABC">Developer Python</a></article>
    <article class="box_offer">
      <a class="js-o-link" href="/ofertas-de-trabajo/oferta-de-trabajo-java-DEF">Java</a>
      <p>Más de 30 días</p>
    </article>
    """
    ofertas = extraer_computrabajo(html, "Tecnología")
    assert len(ofertas) == 1
    assert ofertas[0].titulo == "Developer Python"
    assert ofertas[0].url.startswith("https://ve.computrabajo.com/")


def test_extraer_bumeran_admite_titulo_desde_url():
    html = '<a href="/empleos/desarrollador-python-aviso-123.html"></a>'
    ofertas = extraer_bumeran(html, "Tecnología")
    assert len(ofertas) == 1
    assert ofertas[0].titulo == "Desarrollador Python"


def test_extraer_gentetop_extrae_empresa():
    html = """
    <article><div>
      <a href="/ve/empleo/analista-contable-123">Analista Contable</a>
      <span class="company-name">Empresa Demo</span>
    </div></article>
    """
    ofertas = extraer_gentetop(html, "Administración")
    assert len(ofertas) == 1
    assert ofertas[0].empresa == "Empresa Demo"


class ClienteFalso:
    def __init__(self):
        self.mensajes = []

    async def send_message(self, destino, mensaje, **opciones):
        self.mensajes.append((destino, mensaje, opciones))


def test_motor_comun_envia_aceptadas(monkeypatch):
    cliente = ClienteFalso()
    oferta = base.Oferta(
        "Portal", "Tecnología", "Backend Python", "https://example.test/1"
    )
    monkeypatch.setattr(base, "reservar_hash", Mock(return_value=True))
    marcar = Mock()
    monkeypatch.setattr(base, "marcar_hash", marcar)
    monkeypatch.setattr(
        base,
        "analizar_vacante_detallado",
        Mock(return_value=ResultadoAnalisis(EstadoAnalisis.ACEPTADA, "Prueba")),
    )

    resultado = asyncio.run(base.procesar_ofertas([oferta], cliente))

    assert resultado["aceptadas"] == 1
    assert len(cliente.mensajes) == 1
    marcar.assert_called_once_with(oferta.clave(), "procesado")


def test_motor_comun_deja_error_reintentable(monkeypatch):
    cliente = ClienteFalso()
    oferta = base.Oferta("Portal", "Área", "Puesto", "https://example.test/2")
    monkeypatch.setattr(base, "reservar_hash", Mock(return_value=True))
    marcar = Mock()
    monkeypatch.setattr(base, "marcar_hash", marcar)
    monkeypatch.setattr(
        base,
        "analizar_vacante_detallado",
        Mock(return_value=ResultadoAnalisis(EstadoAnalisis.ERROR, motivo="caído")),
    )

    resultado = asyncio.run(base.procesar_ofertas([oferta], cliente))

    assert resultado["errores"] == 1
    assert cliente.mensajes == []
    marcar.assert_called_once_with(oferta.clave(), "error")


def test_descarga_detecta_intersticial_javascript(monkeypatch):
    respuesta = Mock()
    respuesta.text = '<script>window.location.href="/lander"</script>'
    respuesta.headers = {"Content-Type": "text/html"}
    respuesta.raise_for_status = Mock()
    monkeypatch.setattr(base.requests, "get", Mock(return_value=respuesta))
    with pytest.raises(RuntimeError, match="JavaScript"):
        base.descargar_html("https://example.test")
