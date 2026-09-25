from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from database.db import init_db, verify_db_ddl
from routers.ticket_router import router as ticket_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    verify_db_ddl()
    yield


app = FastAPI(
    title="Sistema de Chamados",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router=ticket_router)

templates = Jinja2Templates(directory="templates")


@app.get("/")
def index():
    return RedirectResponse("/tickets/")
