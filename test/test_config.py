import config


def test_leer_grupos_separa_validos_e_invalidos():
    grupos, invalidos = config._leer_grupos("-1001, texto, -1002")
    assert grupos == [-1001, -1002]
    assert invalidos == ["texto"]


def test_validar_configuracion_detecta_faltantes(monkeypatch):
    monkeypatch.setattr(config, "API_ID", None)
    monkeypatch.setattr(config, "API_HASH", "")
    monkeypatch.setattr(config, "GRUPOS_RELEVANTES", [])
    monkeypatch.setattr(config, "GRUPOS_INVALIDOS", [])
    monkeypatch.setattr(config, "GROQ_KEY", "")
    monkeypatch.setattr(config, "GEMINI_KEY", "")
    assert len(config.validar_configuracion()) == 4


def test_validar_configuracion_acepta_un_proveedor(monkeypatch):
    monkeypatch.setattr(config, "API_ID", 123)
    monkeypatch.setattr(config, "API_HASH", "hash")
    monkeypatch.setattr(config, "GRUPOS_RELEVANTES", [-1001])
    monkeypatch.setattr(config, "GRUPOS_INVALIDOS", [])
    monkeypatch.setattr(config, "GROQ_KEY", "key")
    monkeypatch.setattr(config, "GEMINI_KEY", "")
    assert config.validar_configuracion() == []
