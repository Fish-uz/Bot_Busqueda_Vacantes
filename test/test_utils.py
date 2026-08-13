import os
from utils import generar_hash_mensaje, es_mensaje_repetido, HASH_FILE

def test_hashing_consistencia():
    """Verifica que el mismo texto genere el mismo hash ignorando espacios/mayúsculas"""
    txt1 = "Hola Mundo"
    txt2 = " hola  MUNDO "
    assert generar_hash_mensaje(txt1) == generar_hash_mensaje(txt2)

def test_anti_spam_repetido():
    """Verifica que el sistema detecte un mensaje ya procesado"""
    # Limpiamos el archivo de prueba si existe
    if os.path.exists(HASH_FILE):
        os.remove(HASH_FILE)
    
    mensaje = "Vacante de Programador Python"
    h = generar_hash_mensaje(mensaje)
    
    # Primera vez: No debe ser repetido
    assert es_mensaje_repetido(h) is False
    # Segunda vez: Debe ser repetido
    assert es_mensaje_repetido(h) is True
