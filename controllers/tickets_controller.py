from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from models.chamado import Ticket
from service.tickets_service import TicketService
from utils import get_current_datetime

r = APIRouter()

templates = Jinja2Templates(directory="templates")

service = TicketService()


@r.get("/", response_class=HTMLResponse)
def list_chamados(request: Request):
    tickets = service.find_all()
    return templates.TemplateResponse(
        request, "tickets_list.html", context={"tickets": tickets}
    )


@r.get("/create", response_class=HTMLResponse)
def create_ticket_get(request: Request):
    date, time = get_current_datetime()
    ticket = Ticket(service_date=date, start_time=time)
    return templates.TemplateResponse(request, "create_ticket.html", {"ticket": ticket})


@r.post("/")
def create_ticket(
    ticket: Annotated[Ticket, Form()]
):
    service.create(ticket)
    return RedirectResponse(
        url="/",
        status_code=status.HTTP_303_SEE_OTHER,
    )
