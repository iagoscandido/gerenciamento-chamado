from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from database.db import get_session
from models.ticket_model import Ticket, TicketCreate, TicketFinish, TicketUpdate
from services.ticket_service import TicketService

templates = Jinja2Templates("templates")

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/")
def ticket_index(request: Request, session: SessionDep):
    service = TicketService(session)
    tickets = service.get_all()
    summary = service.get_summary()

    return templates.TemplateResponse(
        request, "tickets/index.html", {"tickets": tickets, "summary": summary}
    )


@router.get("/all")
def get_all_tickets(session: SessionDep):
    tickets = TicketService(session).get_all()

    return tickets


@router.get("/create", response_class=HTMLResponse)
def get_create_ticket(request: Request):
    return templates.TemplateResponse(request, "tickets/create_ticket.html")


@router.post("/", response_class=HTMLResponse)
def create(ticket: Annotated[TicketCreate, Form()], session: SessionDep):

    TicketService(session).create(ticket)

    return RedirectResponse(
        url="/tickets",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.patch("/{ticket_id}", response_model=Ticket)
def update(ticket_id: int, ticket: TicketUpdate, session: SessionDep):
    updated_ticket = TicketService(session).update(ticket_id, ticket)

    if updated_ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket não encontrado",
        )

    return updated_ticket


@router.patch("/{ticket_id}/start_travel", response_model=Ticket)
def start_travel(ticket_id: int, session: SessionDep):
    return TicketService(session).start_travel(ticket_id)


@router.patch("/{ticket_id}/start_service", response_model=Ticket)
def start_service(ticket_id: int, session: SessionDep):
    return TicketService(session).start_service(ticket_id)


@router.patch("/{ticket_id}/finish_service", response_model=Ticket)
def finish_service(ticket_id: int, ticket: TicketFinish, session: SessionDep):
    return TicketService(session).finish_service(ticket_id, ticket)


@router.patch("/{ticket_id}/cancel_service", response_model=Ticket)
def cancel_service(ticket_id: int, session: SessionDep):
    return TicketService(session).cancel_service(ticket_id)


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: int,
    session: SessionDep,
):
    deleted = TicketService(session).delete(ticket_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Ticket não encontrado",
        )


@router.get("/{ticket_id}")
def get_by_id(
    request: Request,
    ticket_id: int,
    session: SessionDep,
):
    ticket = TicketService(session).get_by_id(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket não encontrado",
        )

    return templates.TemplateResponse(request, "tickets/ticket.html", {"ticket": ticket})
