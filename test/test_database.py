import database


def test_reserva_atomica_y_reintento_de_error(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "prueba.db")
    database.inicializar_db()
    assert database.reservar_hash("abc") is True
    assert database.reservar_hash("abc") is False
    database.marcar_hash("abc", "error")
    assert database.reservar_hash("abc") is True
    database.marcar_hash("abc", "procesado")
    assert database.existe_hash("abc") is True
    assert database.reservar_hash("abc") is False


def test_guardar_hash_conserva_compatibilidad(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "prueba.db")
    database.inicializar_db()
    assert database.guardar_hash("abc") is True
    assert database.guardar_hash("abc") is False
