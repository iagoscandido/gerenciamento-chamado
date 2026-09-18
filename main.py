from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import database
from models.chamado import Chamado
from service.chamado import ChamadoService


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


app = FastAPI(title="Sistema de Chamados", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

service = ChamadoService()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
    )


@app.get("/chamados", response_class=HTMLResponse)
def listar_chamados(request: Request):
    chamados = service.find_all()

    return templates.TemplateResponse(
        request,
        "chamados.html",
        {
            "chamados": chamados,
        },
    )


@app.post("/chamados")
def criar_chamado(
    data_atendimento: str = Form(...),
    hora_inicio: str = Form(...),
    hora_fim: str = Form(...),
    valor: float = Form(0.0),
    despesas: float = Form(0.0),
    localidade: str = Form(...),
    contato: str = Form(...),
    cliente_final: str = Form(...),
    cliente: str = Form(...),
    escopo: str = Form(...),
    resumo_tecnico: str = Form(...),
):
    c = Chamado(
        data_atendimento=data_atendimento,
        hora_inicio=hora_inicio,
        hora_fim=hora_fim,
        valor=valor,
        despesas=despesas,
        localidade=localidade,
        contato=contato,
        cliente_final=cliente_final,
        cliente=cliente,
        escopo=escopo,
        resumo_tecnico=resumo_tecnico,
    )

    service.create(c)

    return RedirectResponse(
        url="/",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@app.get("/chamados/novo", response_class=HTMLResponse)
def novo_chamado(request: Request):
    return templates.TemplateResponse(
        request,
        "novo_chamado.html",
    )


@app.get("/chamados/{c_id}", response_class=HTMLResponse)
def visualizar_chamado(request: Request, c_id: int):
    chamado = service.find_by_id(str(c_id))

    if chamado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chamado não encontrado",
        )

    return templates.TemplateResponse(
        request,
        "chamado.html",
        {"chamado": chamado},
    )
