from utils import generar_hash_mensaje


def test_hashing_consistencia():
    assert generar_hash_mensaje("Hola Mundo") == generar_hash_mensaje(" hola  MUNDO ")


def test_hashing_distingue_contenido():
    assert generar_hash_mensaje("Vacante Python") != generar_hash_mensaje("Vacante Java")


def test_hashing_conserva_limites_entre_palabras():
    assert generar_hash_mensaje("AB C") != generar_hash_mensaje("A BC")
