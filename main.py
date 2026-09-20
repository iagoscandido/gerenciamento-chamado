from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import database
from routers.tickets_router import r as tickets_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    database.init_db()
    yield


app = FastAPI(title="Sistema de Chamados", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router=tickets_router, prefix="/tickets")


templates = Jinja2Templates(directory="templates")


@app.get("/")
def index():
    return RedirectResponse("/tickets/")
