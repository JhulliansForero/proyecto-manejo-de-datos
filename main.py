#-----------------------------------------
import os  # módulo para manejar rutas de archivos
from fastapi import FastAPI, Form, Request, File, UploadFile  # FastAPI es el servidor; Form lee formularios; Request lee la petición; File/UploadFile reciben archivos
from fastapi.responses import RedirectResponse, HTMLResponse  # RedirectResponse manda a otra página; HTMLResponse devuelve un HTML
from fastapi.staticfiles import StaticFiles  # sirve los archivos estáticos (los CSS)
from starlette.middleware.sessions import SessionMiddleware  # maneja las sesiones (cookies de login)
from jinja2 import Environment, FileSystemLoader  # motor de plantillas para armar los HTML
from database import init_db, login_usuario, registrar_usuario  # trae las funciones de database.py
from datos import obtener_metricas, CSV_PATH  # trae la función que calcula los datos y la ruta donde se guarda el CSV
#-----------------------------------------


#-----------------------------------------
app = FastAPI()  # crea el servidor web
app.add_middleware(SessionMiddleware, secret_key="smartbite-clave-secreta")  # activa las sesiones con una clave secreta que firma la cookie
#-----------------------------------------


#-----------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # ruta de la carpeta donde está main.py
jinja_env = Environment(  # configura el motor de plantillas Jinja2
    loader=FileSystemLoader(os.path.join(BASE_DIR, "templates")),  # le dice dónde están los HTML
    cache_size=0,  # apaga el caché (necesario por Python 3.14 y hace que los cambios se vean al instante)
)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")  # publica los CSS en la URL /static
init_db()  # crea la tabla de usuarios si todavía no existe
#-----------------------------------------


#-----------------------------------------
# función propia que convierte un HTML en una respuesta para el navegador
def render(template_name: str, **contexto) -> HTMLResponse:
    template = jinja_env.get_template(template_name)  # busca el archivo HTML dentro de templates/
    return HTMLResponse(content=template.render(**contexto))  # lo convierte en texto y lo envía
#-----------------------------------------


#-----------------------------------------
# cuando el navegador entra a "/" lo manda al login
@app.get("/")  # responde a la URL raíz (método GET)
async def raiz():
    return RedirectResponse("/login")  # redirige a /login
#-----------------------------------------


#-----------------------------------------
# muestra el formulario de inicio de sesión
@app.get("/login")  # responde a GET /login
async def get_login():
    return render("login.html")  # devuelve el HTML del login
#-----------------------------------------


#-----------------------------------------
# procesa el formulario de inicio de sesión cuando se envía
@app.post("/login")  # responde a POST /login
async def post_login(request: Request, email: str = Form(...), password: str = Form(...)):  # lee email y password del formulario
    usuario = login_usuario(email, password)  # busca el usuario en la base de datos
    if usuario:  # si lo encontró
        request.session["usuario"] = usuario  # guarda sus datos en la sesión (cookie)
        return RedirectResponse("/inicio", status_code=303)  # lo manda al dashboard
    return render("login.html")  # si no lo encontró, vuelve a mostrar el login
#-----------------------------------------


#-----------------------------------------
# muestra el formulario de registro
@app.get("/registro")  # responde a GET /registro
async def get_registro():
    return render("registro.html")  # devuelve el HTML del registro
#-----------------------------------------


#-----------------------------------------
# procesa el formulario de registro cuando se envía
@app.post("/registro")  # responde a POST /registro
async def post_registro(
    nombre:   str = Form(...),  # lee el campo nombre del formulario
    email:    str = Form(...),  # lee el campo email del formulario
    password: str = Form(...),  # lee el campo password del formulario
    sucursal: str = Form(...),  # lee el campo sucursal del formulario
    rol:      str = Form(...),  # lee el campo rol del formulario
):
    resultado = registrar_usuario(nombre, email, password, sucursal, rol)  # intenta guardar el usuario
    if resultado["ok"]:  # si se guardó correctamente
        return RedirectResponse("/login", status_code=303)  # lo manda al login
    return render("registro.html")  # si hubo error (email repetido), vuelve al registro
#-----------------------------------------


#-----------------------------------------
# muestra el dashboard: vacío si no hay datos, o con datos si ya se cargó el CSV
@app.get("/inicio")  # responde a GET /inicio
async def get_inicio(request: Request):
    usuario = request.session.get("usuario")  # revisa si hay un usuario en la sesión
    if not usuario:  # si no hay sesión
        return RedirectResponse("/login")  # lo manda al login
    if request.session.get("datos_cargados"):  # si el usuario ya subió el CSV
        metricas = obtener_metricas()  # lee el CSV y calcula los datos del dashboard
        return render("inicio_datos.html", **metricas)  # muestra el dashboard con datos
    return render("inicio.html")  # si no hay datos todavía, muestra el dashboard vacío
#-----------------------------------------


#-----------------------------------------
# recibe el archivo CSV que sube el usuario y lo guarda
@app.post("/cargar")  # responde a POST /cargar
async def cargar(request: Request, archivo: UploadFile = File(...)):  # lee el archivo enviado en el formulario
    contenido = await archivo.read()  # lee todo el contenido del archivo subido
    with open(CSV_PATH, "wb") as f:  # abre (o crea) el archivo de datos en el disco
        f.write(contenido)  # guarda el CSV
    request.session["datos_cargados"] = True  # marca en la sesión que ya hay datos cargados
    return RedirectResponse("/inicio", status_code=303)  # vuelve al dashboard, ahora con datos
#-----------------------------------------


#-----------------------------------------
# cierra la sesión del usuario
@app.post("/logout")  # responde a POST /logout
async def logout(request: Request):
    request.session.clear()  # borra todos los datos de la sesión
    return RedirectResponse("/login", status_code=303)  # lo manda al login
#-----------------------------------------
