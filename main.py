from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import database
from controllers.chamados_controller import r as chamados_controller


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


app = FastAPI(title="Sistema de Chamados", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router=chamados_controller, prefix="/chamados")


templates = Jinja2Templates(directory="templates")


@app.get("/")
def index(request: Request):
    return RedirectResponse("/chamados")
