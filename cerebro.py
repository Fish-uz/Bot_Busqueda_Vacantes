import re
from groq import Groq
from config import GROQ_KEY
from utils import Log

# =================================================================
# CONFIGURACIÓN DE CLIENTE
# =================================================================
# Inicializamos el cliente de Groq utilizando la API KEY definida en config
client = Groq(api_key=GROQ_KEY)

def analizar_vacante(texto_mensaje):
    """
    Usa la IA de Groq para determinar si el mensaje es una vacante relevante.
    Analiza el contenido del mensaje frente a perfiles técnicos y administrativos.
    """
    
    # -------------------------------------------------------------
    # DEFINICIÓN DE PERFILES DE EXPERIENCIA (Contexto para la IA)
    # -------------------------------------------------------------

    # Perfil orientado a desarrollo backend y automatización
    perfil_it = "Backend Developer (Python, Django, Flask, FastAPI), Especialista en Automatización (n8n, IA Generativa, SQL), Junior IT, Consultor Odoo."
    
    # Perfil orientado a gestión financiera y procesos administrativos en sector Fintech
    perfil_admin = "Analista de Operaciones Fintech, Medios de Pago, Puntos de venta, Analista Contable, Cuentas por Pagar, Analista de Finanzas, Conciliación Bancaria (AS400, CRM, Profit)."
    
    # -------------------------------------------------------------
    # CONSTRUCCIÓN DEL PROMPT (Instrucciones de reclutamiento)
    # -------------------------------------------------------------

    # Se establece el rol de reclutador experto y los criterios geográficos de Venezuela
    prompt = f"""
    Actúa como un agente experto para encontrar vacantes para Frank Uzcátegui en Venezuela.
    Minimo deben de pedir titulo universitario de (informatica, sistemas, administracion, contabilidad, finanzas)
    No nos interesa, trabajos de atencion al cliente, ventas, marketing, diseño grafico, recursos humanos, ni vacantes que pidan titulo universitario de cualquier otra rama que no sea sistemas, informatica, contabilidad o administracion
    CRITERIOS DE UBICACIÓN:
    - Prioridad: Caracas, Miranda, Distrito Capital o vacantes 100% Remotas.
    - Ignorar: Vacantes presenciales en otros estados (Valencia, Maracaibo, etc.).

    PERFILES DE INTERÉS:
    1. TECNOLOGÍA: {perfil_it}
    2. ADMINISTRATIVO: {perfil_admin}

    INSTRUCCIONES:
    - Responde 'TRUE - [razón]' si coincide en perfil y ubicación.
    - Responde 'FALSE - [razón]' si no coincide o es alguien buscando empleo.
    - Responde 'FALSE - [razón]' si tienes dudas
    - Responde 'FALSE - [razón]' si piden titulo universitario de cualquier otra rama que no sea sistemas, informatica, contabilidad o administracion
    - Estas buscando vacante para mi, por lo que no nos interesa si otra persona esta buscando vacantes, no queremos informacion corta o vacia.
    - Debes enviarme la vacante solo si coincide un 80% con los perfiles de interes
    - La razón debe ser de máximo 10 palabras.
    - Responde ÚNICAMENTE en ese formato.

    MENSAJE A ANALIZAR:
    "{texto_mensaje}"
    """

    try:
        Log.info("IA (Groq) analizando relevancia...")
        
        # -------------------------------------------------------------
        # LLAMADA A LA API DE GROQ
        # -------------------------------------------------------------
        
        # Usamos el modelo Llama 3.1 8B por su alta velocidad y eficiencia en texto
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
        )

        # Limpiamos la respuesta para facilitar la validación
        resultado = completion.choices[0].message.content.strip().upper()
        Log.info(f"Decisión IA: {resultado}")

        # -------------------------------------------------------------
        # VALIDACIÓN DE RESULTADO (Lógica Booleana)
        # -------------------------------------------------------------
        # Usamos expresiones regulares para confirmar la presencia de 'TRUE' como palabra exacta
        if re.search(r"\bTRUE\b", resultado):
            return True
        return False
    
    except Exception as e:
        # Captura de errores de conexión o límites de API
        Log.error(f"Error en Cerebro Groq: {e}")
        return False