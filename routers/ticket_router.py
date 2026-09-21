from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from models.ticket import Ticket, TicketStatus
from services.ticket_service import TicketService

templates = Jinja2Templates("templates")

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)

service = TicketService()


@router.get("/")
def ticket_index(request: Request):
    tickets = service.find_all()

    return templates.TemplateResponse(request, "tickets/index.html", {"tickets": tickets})


@router.get("/new")
def render_new_ticket_form(request: Request):

    return templates.TemplateResponse(
        request,
        "tickets/new.html"
    )


@router.post("/")
def create_ticket(
    service_date: Annotated[str, Form()],
    contractor: Annotated[str, Form()],
    value: Annotated[float, Form()],
    address: Annotated[str, Form()],
    client: Annotated[str, Form()],
):

    ticket = Ticket(
        service_date=service_date,
        contractor=contractor,
        value=value,
        address=address,
        client=client,
        status=TicketStatus.OPEN,
    )

    created = service.create(ticket)

    if created is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error creating ticket",
        )

    return RedirectResponse(
        url="/tickets",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/{ticket_id}")
def get_ticket_by_id(request: Request, ticket_id: int):
    ticket = service.find_by_id(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )


@router.get("/{ticket_id}/detail")
def render_ticket_detail(request: Request, ticket_id: int):

    ticket = service.find_by_id(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return templates.TemplateResponse(request, "tickets/ticket.html", {"ticket": ticket})


@router.patch("/{ticket_id}/start-travel")
def start_travel(ticket_id: int):
    ticket = service.start_travel(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="error starting travel for this ticket",
        )

    return RedirectResponse(
        url=f"/tickets/{ticket_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )
