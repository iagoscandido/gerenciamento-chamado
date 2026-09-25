from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from database.db import get_session
from models.ticket_model import Ticket, TicketCreate, TicketStatus

templates = Jinja2Templates("templates")

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)


@router.get("/")
def ticket_index(request: Request):
    return templates.TemplateResponse(request, "tickets/index.html", {})


@router.get("/{ticket_id}", response_model=Ticket)
def find_ticket_by_id(
    ticket_id: int, session: Annotated[Session, Depends(get_session)]
):
    ticket = session.get(Ticket, ticket_id)

    if not Ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return ticket


@router.get("/all")
def get_all_tickets(session: Annotated[Session, Depends(get_session)]):
    statement = select(Ticket)
    tickets = session.exec(statement).all()

    return tickets


@router.post("/", response_model=Ticket, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket: TicketCreate,
    session: Annotated[Session, Depends(get_session)],
):
    db_ticket = Ticket.model_validate(ticket)

    session.add(db_ticket)
    session.commit()
    session.refresh(db_ticket)

    return db_ticket
