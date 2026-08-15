import asyncio
from types import SimpleNamespace
from unittest.mock import Mock

import monitor
from cerebro import EstadoAnalisis, ResultadoAnalisis


class EventoFalso:
    chat_id = -1001
    raw_text = "Vacante Python remota"
    photo = None
    message = SimpleNamespace(id=10)

    def __init__(self):
        self.reenviado = False

    async def get_chat(self):
        return SimpleNamespace(title="Grupo de prueba")

    async def forward_to(self, _destino):
        self.reenviado = True


def test_handler_reenvia_y_marca_resultado(monkeypatch, tmp_path):
    evento = EventoFalso()
    monitor.cache_nombres_grupos.clear()
    monkeypatch.setattr(monitor, "OCR_LOG_PATH", tmp_path / "ocr.log")
    monkeypatch.setattr(monitor, "reservar_hash", Mock(return_value=True))
    marcar = Mock()
    monkeypatch.setattr(monitor, "marcar_hash", marcar)
    monkeypatch.setattr(
        monitor,
        "analizar_vacante_detallado",
        Mock(return_value=ResultadoAnalisis(EstadoAnalisis.ACEPTADA, "Prueba")),
    )

    asyncio.run(monitor.manejador_de_vacantes(evento))

    assert evento.reenviado is True
    marcar.assert_called_once_with(monitor.generar_hash_mensaje(evento.raw_text), "procesado")
    contenido = (tmp_path / "ocr.log").read_text(encoding="utf-8")
    assert evento.raw_text not in contenido


def test_handler_marca_error_para_reintento(monkeypatch):
    evento = EventoFalso()
    monitor.cache_nombres_grupos.clear()
    monkeypatch.setattr(monitor, "reservar_hash", Mock(return_value=True))
    marcar = Mock()
    monkeypatch.setattr(monitor, "marcar_hash", marcar)
    monkeypatch.setattr(
        monitor,
        "analizar_vacante_detallado",
        Mock(return_value=ResultadoAnalisis(EstadoAnalisis.ERROR, motivo="caído")),
    )

    asyncio.run(monitor.manejador_de_vacantes(evento))

    assert evento.reenviado is False
    marcar.assert_called_once_with(monitor.generar_hash_mensaje(evento.raw_text), "error")
