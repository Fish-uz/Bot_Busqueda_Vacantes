import sqlite3
import os
from datetime import datetime
from utils import Log

DB_NAME = "vacantes_data.db"

def obtener_conexion():
    """Establece conexión con la base de datos SQLite."""
    return sqlite3.connect(DB_NAME)

def inicializar_db():
    """
    Crea las tablas necesarias y gestiona la limpieza mensual.
    """
    mes_actual = datetime.now().strftime("%Y-%m")
    conn = obtener_conexion()
    cursor = conn.cursor()

    # Tabla para metadatos (para rastrear el mes actual)
    cursor.execute('''CREATE TABLE IF NOT EXISTS sistema (
                        clave TEXT PRIMARY KEY,
                        valor TEXT)''')

    # Verificar el mes guardado
    cursor.execute("SELECT valor FROM sistema WHERE clave = 'mes_registro'")
    resultado = cursor.fetchone()

    if resultado is None:
        # Primera ejecución
        cursor.execute("INSERT INTO sistema (clave, valor) VALUES ('mes_registro', ?)", (mes_actual,))
    elif resultado[0] != mes_actual:
        # Cambio de mes detectado: Limpiar tabla de hashes
        Log.alerta(f"Nuevo mes detectado ({mes_actual}). Limpiando base de datos de hashes...")
        cursor.execute("DROP TABLE IF EXISTS hashes")
        cursor.execute("UPDATE sistema SET valor = ? WHERE clave = 'mes_registro'", (mes_actual,))

    # Tabla de hashes anti-spam
    cursor.execute('''CREATE TABLE IF NOT EXISTS hashes (
                        hash_msg TEXT PRIMARY KEY,
                        fecha TEXT)''')
    
    conn.commit()
    conn.close()

def guardar_hash(hash_texto):
    """Guarda un hash en la base de datos."""
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO hashes (hash_msg, fecha) VALUES (?, ?)", (hash_texto, fecha_hoy))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # El hash ya existe
        conn.close()
        return False
    except Exception as e:
        Log.error(f"Error en DB al guardar hash: {e}")
        return False

def existe_hash(hash_texto):
    """Verifica si el hash ya existe."""
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM hashes WHERE hash_msg = ?", (hash_texto,))
    existe = cursor.fetchone() is not None
    conn.close()
    return existe
