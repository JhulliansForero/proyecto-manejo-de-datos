import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from jinja2 import Environment, FileSystemLoader

from database import init_db, login_usuario, registrar_usuario

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="smartbite-clave-secreta")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

jinja_env = Environment(
    loader=FileSystemLoader(os.path.join(BASE_DIR, "templates")),
    cache_size=0,
)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

init_db()


def render(template_name: str, **contexto) -> HTMLResponse:
    template = jinja_env.get_template(template_name)
    return HTMLResponse(content=template.render(**contexto))


@app.get("/")
async def raiz():
    return RedirectResponse("/login")


@app.get("/login")
async def get_login(ok: str = None):
    return render("login.html")


@app.post("/login")
async def post_login(request: Request, email: str = Form(...), password: str = Form(...)):
    usuario = login_usuario(email, password)
    if usuario:
        request.session["usuario"] = usuario
        return RedirectResponse("/inicio", status_code=303)
    return render("login.html")


@app.get("/registro")
async def get_registro():
    return render("registro.html")


@app.post("/registro")
async def post_registro(
    nombre:   str = Form(...),
    email:    str = Form(...),
    password: str = Form(...),
    sucursal: str = Form(...),
    rol:      str = Form(...),
):
    resultado = registrar_usuario(nombre, email, password, sucursal, rol)
    if resultado["ok"]:
        return RedirectResponse("/login", status_code=303)
    return render("registro.html")


@app.get("/inicio")
async def get_inicio(request: Request):
    usuario = request.session.get("usuario")
    if not usuario:
        return RedirectResponse("/login")
    return render("inicio.html")


@app.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
