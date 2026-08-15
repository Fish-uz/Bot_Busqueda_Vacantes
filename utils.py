import hashlib


def generar_hash_mensaje(texto):
    """Genera una huella estable conservando los límites entre palabras."""
    texto_normalizado = " ".join(texto.casefold().split())
    return hashlib.sha256(texto_normalizado.encode("utf-8")).hexdigest()
