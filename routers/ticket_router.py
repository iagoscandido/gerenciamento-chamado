from services.ticket_service import TicketService
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from database.db import get_session
from models.ticket_model import Ticket, TicketCreate

templates = Jinja2Templates("templates")

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/")
def ticket_index(request: Request):
    return templates.TemplateResponse(request, "tickets/index.html", {})


@router.get("/all")
def get_all_tickets(session: SessionDep):
    tickets = TicketService(session).get_all()

    return tickets


@router.get("/summary", response_class=HTMLResponse)
def ticket_summary(
    request: Request,
    session: SessionDep,
):
    summary = TicketService(session).get_summary()

    return templates.TemplateResponse(
        request=request,
        name="tickets/summary.html",
        context={"summary": summary},
    )


@router.post("/", response_model=Ticket, status_code=status.HTTP_201_CREATED)
def create(
    ticket: TicketCreate,
    session: SessionDep,
):
    create_ticket = TicketService(session).create(ticket)

    return create_ticket


@router.get("/{ticket_id}", response_model=Ticket)
def get_by_id(
    ticket_id: int,
    session: SessionDep,
):
    ticket = TicketService(session).get_by_id(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket não encontrado",
        )

    return ticket
