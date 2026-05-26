import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "smartbite.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre         TEXT    NOT NULL,
                email          TEXT    NOT NULL UNIQUE,
                password       TEXT    NOT NULL,
                sucursal       TEXT    NOT NULL,
                rol            TEXT    NOT NULL,
                fecha_registro TEXT    DEFAULT (date('now'))
            )
        """)
        con.commit()

        

def registrar_usuario(nombre, email, password, sucursal, rol) -> dict:
    try:
        with get_connection() as con:
            con.execute(
                "INSERT INTO usuarios (nombre, email, password, sucursal, rol) VALUES (?,?,?,?,?)",
                (nombre, email, password, sucursal, rol)
            )
            con.commit()
        return {"ok": True}
    except sqlite3.IntegrityError:
        return {"ok": False, "error": "Ese email ya está registrado."}
    


def login_usuario(email, password) -> dict | None:
    with get_connection() as con:
        row = con.execute(
            "SELECT id, nombre, email, sucursal, rol FROM usuarios WHERE email=? AND password=?",
            (email, password)
        ).fetchone()
    if row:
        return {"id": row[0], "nombre": row[1], "email": row[2], "sucursal": row[3], "rol": row[4]}
    return None
