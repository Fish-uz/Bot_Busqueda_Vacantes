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
    Eres un Filtro de Reclutamiento de alta precisión para Frank Uzcátegui (Venezuela).
    Tu misión es descartar el 99% de los mensajes y solo aceptar vacantes reales que cumplan estrictamente:

    REGLAS DE ORO (Si no se cumple, responde FALSE):
    1. UBICACIÓN: Solo Caracas, Miranda, Distrito Capital o 100% Remoto. 
       - DESCARTA: Valencia, Maracaibo, Aragua o cualquier otro estado. Tambien ubicaciones como: Charallave, Santa Teresa del Tuy, Valles del Tuy.
    2. TÍTULO REQUERIDO: Debe mencionar explícitamente: Sistemas, Informática, Computación, Administración, Banca, Medios de Pagos, Contabilidad o Finanzas.
       - DESCARTA: Médicos, Enfermeros, Abogados, Educación, Vendedor, Ventas puras.
    3. ROL PROHIBIDO: No aceptes: Ventas, Marketing, Diseño, RRHH, Atención al Cliente, Visitador Médico, Cajeros, Operarios.
    4. NO BUSCADORES: Si el texto es de alguien BUSCANDO empleo, responde FALSE. Solo buscamos EMPRESAS contratando.
    5. Responder FALSE los siguientes Perfiles: "Talento Humano", "Recursos Humanos", "Gestion del Talento", "Vendedor",
    6. Responder FALSE cuando esten ofreciendo servicios

    PERFILES DE REFERENCIA PARA MATCH (Mínimo 80%):
    - IT: {perfil_it}
    - ADMIN/CONTABLE: {perfil_admin}

    MENSAJE A ANALIZAR:
    "{texto_mensaje}"

    FORMATO DE RESPUESTA (ESTRICTO):
    - Si cumple TODO: TRUE - [razón corta de por qué cumple]
    - Si falla en ALGO o es SPAM: FALSE - [razón de 1 a 12 palabras del descarte]
    
    INSTRUCCIÓN FINAL: Si tienes la más mínima duda o la información está incompleta, responde FALSE. No adivines.
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