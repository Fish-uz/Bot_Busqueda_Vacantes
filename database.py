import sqlite3
from datetime import datetime

from config import DB_PATH, logger


def obtener_conexion():
    conexion = sqlite3.connect(DB_PATH, timeout=10)
    conexion.execute("PRAGMA busy_timeout = 10000")
    return conexion


def inicializar_db():
    mes_actual = datetime.now().strftime("%Y-%m")
    with obtener_conexion() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS sistema (clave TEXT PRIMARY KEY, valor TEXT)"
        )
        resultado = conn.execute(
            "SELECT valor FROM sistema WHERE clave = 'mes_registro'"
        ).fetchone()
        if resultado and resultado[0] != mes_actual:
            logger.warning("Nuevo mes: se reinicia el historial anti-duplicados")
            conn.execute("DROP TABLE IF EXISTS hashes")
        conn.execute(
            "INSERT OR REPLACE INTO sistema (clave, valor) VALUES ('mes_registro', ?)",
            (mes_actual,),
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS hashes (
                   hash_msg TEXT PRIMARY KEY,
                   fecha TEXT NOT NULL,
                   estado TEXT NOT NULL DEFAULT 'procesado'
               )"""
        )
        columnas = {fila[1] for fila in conn.execute("PRAGMA table_info(hashes)")}
        if "estado" not in columnas:
            conn.execute(
                "ALTER TABLE hashes ADD COLUMN estado TEXT NOT NULL DEFAULT 'procesado'"
            )


def reservar_hash(hash_texto):
    """Reserva atómicamente un mensaje nuevo o uno que terminó con error."""
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with obtener_conexion() as conn:
            cursor = conn.execute(
                """INSERT INTO hashes (hash_msg, fecha, estado)
                   VALUES (?, ?, 'pendiente')
                   ON CONFLICT(hash_msg) DO UPDATE SET
                       fecha = excluded.fecha,
                       estado = 'pendiente'
                   WHERE hashes.estado = 'error'""",
                (hash_texto, fecha),
            )
            return cursor.rowcount == 1
    except sqlite3.Error:
        logger.exception("No se pudo reservar el hash")
        return False


def marcar_hash(hash_texto, estado):
    if estado not in {"procesado", "error"}:
        raise ValueError(f"Estado de hash inválido: {estado}")
    with obtener_conexion() as conn:
        conn.execute(
            "UPDATE hashes SET estado = ?, fecha = ? WHERE hash_msg = ?",
            (estado, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), hash_texto),
        )


def guardar_hash(hash_texto):
    """Compatibilidad: reserva y marca inmediatamente como procesado."""
    if not reservar_hash(hash_texto):
        return False
    marcar_hash(hash_texto, "procesado")
    return True


def existe_hash(hash_texto):
    with obtener_conexion() as conn:
        fila = conn.execute(
            "SELECT estado FROM hashes WHERE hash_msg = ?", (hash_texto,)
        ).fetchone()
    return fila is not None and fila[0] != "error"
