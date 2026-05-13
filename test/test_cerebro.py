from cerebro import analizar_vacante

def test_ia_reconoce_perfil():
    # Probamos con un mensaje que la IA DEBE captar según tus CVs [cite: 5, 15, 142]
    mensaje = "Buscamos Analista de Cuentas por Pagar en Caracas. Manejo de Profit y Excel."
    resultado = analizar_vacante(mensaje)
    assert resultado is True, "La IA debería haber aceptado esta vacante contable"

def test_ia_rechaza_basura():
    mensaje = "Se vende comida para perros en San Bernardino"
    resultado = analizar_vacante(mensaje)
    assert resultado is False, "La IA debería haber rechazado publicidad"