from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from models.ticket_model import Ticket
from service.tickets_service import TicketService

r = APIRouter()

templates = Jinja2Templates(directory="templates")

service = TicketService()


@r.get("/", response_class=HTMLResponse)
def tickets_page(request: Request):
    return templates.TemplateResponse(
        request,
        "tickets/index.html",
    )


@r.get("/current", response_class=HTMLResponse)
def current_ticket(request: Request):
    ticket = service.find_active()

    if ticket is None:
        return templates.TemplateResponse(
            request,
            "tickets/no_active.html",
        )

    return templates.TemplateResponse(
        request,
        "tickets/active.html",
        {"ticket": ticket},
    )


@r.get("/all", response_class=HTMLResponse)
def list_tickets(request: Request):
    tickets = service.find_all()
    return templates.TemplateResponse(
        request, "tickets/list.html", {"tickets": tickets}
    )


@r.get("/new", response_class=HTMLResponse)
def new_ticket(request: Request):
    active_ticket = service.find_active()

    if active_ticket is not None:
        return RedirectResponse(
            url="/tickets/",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    now = datetime.now()

    return templates.TemplateResponse(
        request,
        "tickets/new.html",
        {
            "service_date": now.strftime("%Y-%m-%d"),
            "start_time": now.strftime("%H:%M"),
        },
    )


@r.post("/")
def create_ticket(
    request: Request,
    client: Annotated[str, Form()],
    address: Annotated[str, Form()],
):
    active_ticket = service.find_active()

    if active_ticket is not None:
        return templates.TemplateResponse(
            request,
            "tickets/active.html",
            {"ticket": active_ticket},
        )

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M")

    ticket = Ticket(service_date=date, start_time=time, client=client, address=address)

    t_id = service.create(ticket)

    ticket.id = t_id

    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={
            "HX-Location": "/",
        },
    )


@r.get("/{ticket_id}/detail", response_class=HTMLResponse)
def ticket_detail(
    request: Request,
    ticket_id: int,
):
    ticket = service.find_by_id(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chamado não encontrado",
        )

    return templates.TemplateResponse(
        request,
        "tickets/detail.html",
        {"ticket": ticket},
    )


@r.patch("/{ticket_id}/finish", response_class=HTMLResponse)
def finish_ticket(
    request: Request,
    ticket_id: int,
):
    ticket = service.find_by_id(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket não encontrado",
        )

    ticket.end_time = datetime.now().strftime("%H:%M")

    updated = service.update(ticket_id, ticket)

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível finalizar o chamado",
        )

    return templates.TemplateResponse(
        request,
        "tickets/no_active.html",
    )
