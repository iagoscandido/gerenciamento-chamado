from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from models.ticket_model import Ticket, TicketStatus


templates = Jinja2Templates("templates")

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)


@router.get("/")
def ticket_index(request: Request):
    return templates.TemplateResponse(request, "tickets/index.html", {})
