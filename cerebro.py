import re
import google.generativeai as genai
from groq import Groq
from config import GROQ_KEY, GEMINI_KEY
from utils import Log

# =================================================================
# CONFIGURACIÓN DE CLIENTES (Multimodal)
# =================================================================
# Groq para velocidad (Llama 3.1)
groq_client = Groq(api_key=GROQ_KEY)

# Gemini como Fallback (Respaldo)
genai.configure(api_key=GEMINI_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

PERFIL_IT = "Backend Developer (Python, Django, Flask, FastAPI), Especialista en Automatización (n8n, IA Generativa, SQL), Junior IT, Consultor Odoo."
PERFIL_ADMIN = "Analista de Operaciones Fintech, Medios de Pago, Puntos de venta, Analista Contable, Cuentas por Pagar, Analista de Finanzas, Conciliación Bancaria (AS400, CRM, Profit)."

def generar_prompt(texto_mensaje):
    return f"""
    Eres un Filtro de Reclutamiento de alta precisión para Frank Uzcátegui (Venezuela).
    Tu misión es descartar el 99% de los mensajes y solo aceptar vacantes reales que cumplan estrictamente:

    REGLAS DE ORO:
    1. UBICACIÓN: Solo Caracas, Miranda, Distrito Capital o 100% Remoto. DESCARTA: Valencia, Maracaibo, Aragua, Valles del Tuy.
    2. TÍTULO: Sistemas, Informática, Computación, Administración, Banca, Medios de Pagos, Contabilidad o Finanzas.
    3. ROL PROHIBIDO: Ventas, Marketing, Diseño, RRHH, Atención al Cliente, Visitador Médico, Cajeros, Operarios.
    4. NO BUSCADORES: Solo EMPRESAS contratando.
    5. NO SERVICIOS: Responder FALSE si ofrecen servicios.

    MATCH PERFILES:
    - IT: {PERFIL_IT}
    - ADMIN/CONTABLE: {PERFIL_ADMIN}

    MENSAJE: "{texto_mensaje}"

    RESPONDE SOLO EN ESTE FORMATO:
    DECISION: [TRUE/FALSE]
    MOTIVO: [Breve explicación]
    """

def analizar_vacante(texto_mensaje):
    """
    Intenta analizar con Groq. Si falla, usa Gemini como respaldo.
    """
    prompt = generar_prompt(texto_mensaje)

    # --- INTENTO 1: GROQ ---
    try:
        Log.info("IA (Groq) analizando...")
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
        )
        resultado = completion.choices[0].message.content.strip().upper()
        return _validar_resultado(resultado, "Groq")

    except Exception as e:
        Log.alerta(f"Groq falló: {e}. Intentando con Gemini (Fallback)...")
        
        # --- INTENTO 2: GEMINI (FALLBACK) ---
        try:
            response = gemini_model.generate_content(prompt)
            resultado = response.text.strip().upper()
            return _validar_resultado(resultado, "Gemini")
        except Exception as e_gemini:
            Log.error(f"Error crítico: Ambos motores de IA fallaron. {e_gemini}")
            return False

def _validar_resultado(resultado, motor):
    """Lógica común para interpretar la respuesta de cualquier IA."""
    Log.info(f"Decisión {motor}: {resultado}")
    if "DECISION: TRUE" in resultado or "DECISION:TRUE" in resultado:
        return True
    return False