from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from database.db import init_db
from routers.ticket_router import router as ticket_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Sistema de Chamados",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router=ticket_router)

templates = Jinja2Templates(directory="templates")


@app.get("/")
def index():
    return RedirectResponse("/tickets/")
