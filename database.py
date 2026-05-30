#-----------------------------------------
import sqlite3  # módulo de Python para manejar bases de datos SQLite
import os        # módulo para construir rutas de archivos
#-----------------------------------------


#-----------------------------------------
# construye la ruta completa del archivo de base de datos, en la misma carpeta que database.py
DB_PATH = os.path.join(os.path.dirname(__file__), "smartbite.db")
#-----------------------------------------


#-----------------------------------------
# función que abre (o crea) la conexión con la base de datos
def get_connection():
    return sqlite3.connect(DB_PATH)  # abre el archivo smartbite.db y devuelve la conexión
#-----------------------------------------


#-----------------------------------------
# función que crea la tabla de usuarios la primera vez que corre la app
def init_db():
    with get_connection() as con:  # abre la conexión y la cierra sola al terminar
        con.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,  -- número único que se asigna solo
                nombre         TEXT    NOT NULL,                   -- texto obligatorio
                email          TEXT    NOT NULL UNIQUE,            -- obligatorio y no se puede repetir
                password       TEXT    NOT NULL,                   -- texto obligatorio
                sucursal       TEXT    NOT NULL,                   -- texto obligatorio
                rol            TEXT    NOT NULL,                   -- texto obligatorio
                fecha_registro TEXT    DEFAULT (date('now'))       -- se llena solo con la fecha de hoy
            )
        """)  # crea la tabla solo si todavía no existe
        con.commit()  # confirma y guarda los cambios en la base de datos
#-----------------------------------------


#-----------------------------------------
# función que guarda un usuario nuevo en la base de datos
def registrar_usuario(nombre, email, password, sucursal, rol) -> dict:
    try:  # intenta ejecutar el guardado
        with get_connection() as con:  # abre la conexión
            con.execute(
                "INSERT INTO usuarios (nombre, email, password, sucursal, rol) VALUES (?,?,?,?,?)",  # inserta una fila nueva; los ? son huecos seguros
                (nombre, email, password, sucursal, rol)  # valores reales que reemplazan a los ?
            )
            con.commit()  # confirma y guarda el nuevo usuario
        return {"ok": True}  # si todo salió bien, avisa que se registró
    except sqlite3.IntegrityError:  # se activa si el email ya existe (la columna es UNIQUE)
        return {"ok": False, "error": "Ese email ya está registrado."}  # avisa el error
#-----------------------------------------


#-----------------------------------------
# función que busca un usuario por su email y contraseña (para el login)
def login_usuario(email, password) -> dict | None:
    with get_connection() as con:  # abre la conexión
        row = con.execute(
            "SELECT id, nombre, email, sucursal, rol FROM usuarios WHERE email=? AND password=?",  # busca al usuario con ese email y contraseña
            (email, password)  # valores reales que reemplazan a los ?
        ).fetchone()  # trae solo una fila (o None si no encuentra nada)
    if row:  # si encontró un usuario
        return {"id": row[0], "nombre": row[1], "email": row[2], "sucursal": row[3], "rol": row[4]}  # devuelve sus datos como diccionario
    return None  # si no encontró nada, devuelve None
#-----------------------------------------
