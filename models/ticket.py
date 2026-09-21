from enum import StrEnum

from pydantic import BaseModel


class TicketStatus(StrEnum):
    OPEN = "open"
    ON_TRAVEL = "on_travel"
    ON_PROGRESS = "on_progress"
    FINISHED = "finished"


class Ticket(BaseModel):
    id: int | None = None
    protocol: str | None = None
    service_date: str
    start_travel: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    client: str
    address: str
    value: float
    contractor: str
    status: TicketStatus
    created_at: str | None = None
    updated_at: str | None = None
