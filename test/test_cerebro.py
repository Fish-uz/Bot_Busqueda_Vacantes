from unittest.mock import Mock

import cerebro


def test_interpreta_respuesta_aceptada():
    resultado = cerebro._interpretar_resultado(
        "DECISION: TRUE\nMOTIVO: Cumple el perfil", "Prueba"
    )
    assert resultado.aceptada
    assert resultado.motivo == "Cumple el perfil"


def test_respuesta_fuera_de_contrato_es_error():
    resultado = cerebro._interpretar_resultado("TRUE - parece válida", "Prueba")
    assert resultado.estado is cerebro.EstadoAnalisis.ERROR


def test_fallback_se_usa_si_groq_falla(monkeypatch):
    monkeypatch.setattr(cerebro, "GROQ_KEY", "groq")
    monkeypatch.setattr(cerebro, "GEMINI_KEY", "gemini")
    groq = Mock(side_effect=RuntimeError("sin conexión"))
    gemini = Mock(return_value="DECISION: FALSE\nMOTIVO: publicidad")
    monkeypatch.setattr(cerebro, "_analizar_con_groq", groq)
    monkeypatch.setattr(cerebro, "_analizar_con_gemini", gemini)
    resultado = cerebro.analizar_vacante_detallado("mensaje")
    assert resultado.estado is cerebro.EstadoAnalisis.RECHAZADA
    groq.assert_called_once()
    gemini.assert_called_once()


def test_fallo_total_no_se_confunde_con_rechazo(monkeypatch):
    monkeypatch.setattr(cerebro, "GROQ_KEY", "groq")
    monkeypatch.setattr(cerebro, "GEMINI_KEY", "")
    monkeypatch.setattr(
        cerebro, "_analizar_con_groq", Mock(side_effect=RuntimeError("caído"))
    )
    resultado = cerebro.analizar_vacante_detallado("mensaje")
    assert resultado.estado is cerebro.EstadoAnalisis.ERROR
    assert cerebro.analizar_vacante("mensaje") is False
