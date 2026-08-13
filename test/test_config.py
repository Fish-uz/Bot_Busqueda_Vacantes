import os
from dotenv import load_dotenv

def test_env_variables_exist():
    """Prueba que las variables de entorno necesarias estén cargadas"""
    load_dotenv()
    
    assert os.getenv("TELEGRAM_API_ID") is not None, "Falta TELEGRAM_API_ID en el .env"
    assert os.getenv("TELEGRAM_API_HASH") is not None, "Falta TELEGRAM_API_HASH en el .env"
    assert os.getenv("GROQ_API_KEY") is not None, "Falta GROQ_API_KEY en el .env"
    assert os.getenv("GEMINI_API_KEY") is not None, "Falta GEMINI_API_KEY en el .env"