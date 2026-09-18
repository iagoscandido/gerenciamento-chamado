from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from models.chamado import Chamado
from service.chamado import ChamadoService

r = APIRouter()

templates = Jinja2Templates(directory="templates")

service = ChamadoService()


@r.get("/", response_class=HTMLResponse)
def list_chamados(request: Request):
    chamados = service.find_all()
    return templates.TemplateResponse(
        request, "chamados.html", context={"chamados": chamados}
    )


@r.get("/novo", response_class=HTMLResponse)
def create_chamado_view(request: Request):
    return templates.TemplateResponse(request, "novo_chamado.html", {"chamado": Chamado()})


@r.get("/{c_id}", response_class=HTMLResponse)
def get_chamado(request: Request, c_id: int):
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


@r.post("/")
def create_chamado(
    c: Annotated[Chamado, Form()]
):
    is_created = service.create(c)

    if is_created:
        return RedirectResponse(
            url="/",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return None
