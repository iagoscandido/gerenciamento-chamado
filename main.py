from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse
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


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


# @app.get("/chamados")
# def listar_chamados(request: Request):
#     chamados = ChamadoService.find_all()
#     return templates.TemplateResponse(request, "chamados/listar_chamados.html", context={
#         "chamados": chamados
#     })


@app.get("/chamados/novo", response_class=HTMLResponse)
def novo_chamado(request: Request):
    return templates.TemplateResponse(
        request,
        "chamados/novo.html",
    )


@app.post("/api/chamados")
def criar_chamado():
    c = Chamado(data_atendimento="2026-09-17",
                hora_inicio="08:00",
                hora_fim="10:30",
                valor=250.00,
                despesas=50.00,
                localidade="Rio de Janeiro",
                contato="João Silva",
                cliente_final="Empresa XYZ",
                cliente="Cliente ABC",
                escopo="Manutenção de equipamento",
                resumo_tecnico="Foi realizada manutenção preventiva e substituição de componentes.",)
    chamado_id = database.create(c
                                 )

    return {
        "id": chamado_id,
        "message": "Chamado criado com sucesso",
    }


@app.get("/api/chamados")
def listar_chamados():
    c = database.find_all()

    return {
        "chamados": c
    }


@app.get("/api/chamados/{c_id}")
def localizar_chamado_por_id(c_id: int):
    c = database.find_by_id(str(c_id))

    if c is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chamado não encontrado",
        )

    return {
        "chamado": c
    }
