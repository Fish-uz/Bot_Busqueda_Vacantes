import pytest
from unittest.mock import patch, MagicMock
import cerebro

# Simulación de un error de conexión o API Key inválida
def test_ia_manejo_error_elegante():
    """
    Simula que Groq falla. El bot debe manejarlo con 'elegancia'
    devolviendo False (descarte seguro) en lugar de romper la app.
    """
    with patch('groq.resources.chat.completions.Completions.create') as mock_groq:
        # Obligamos al mock a lanzar una excepción (Error de conexión)
        mock_groq.side_effect = Exception("API Key Expirada o Error de Red")
        
        # Ejecutamos la función. 
        # SI NO HAY ELEGANCIA: El programa se detiene (Crash)
        # SI HAY ELEGANCIA: La función atrapa el error y devuelve False
        try:
            resultado = cerebro.analizar_vacante("Busco programador")
            assert resultado is False
            print("\n[OK] El bot manejó el error sin romperse.")
        except Exception as e:
            pytest.fail(f"El bot se bloqueó (Crash): {e}")

def test_ia_json_mock():
    """
    Simula una respuesta exitosa de la IA.
    """
    with patch('groq.resources.chat.completions.Completions.create') as mock_groq:
        # Creamos una estructura similar a la que devuelve la API real
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "TRUE - Cumple con el perfil IT"
        mock_groq.return_value = mock_response
        
        resultado = cerebro.analizar_vacante("Vacante Python Caracas")
        assert resultado is True
