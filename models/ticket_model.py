from datetime import UTC, date, datetime, time
from enum import StrEnum

from sqlalchemy import Enum
from sqlmodel import Field, SQLModel


class TicketStatus(StrEnum):
    SCHEDULED = "scheduled"
    ON_TRAVEL = "on_travel"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    CANCELED = "canceled"


class Ticket(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    service_date: date
    service_time: time

    contractor: str
    client: str
    address: str

    description: str
    value: float

    travel_start_time: time | None = None
    service_start_time: time | None = None

    service_finish_time: time | None = None
    technical_summary: str | None = None

    status: TicketStatus = Field(
        default=TicketStatus.SCHEDULED,
        sa_type=Enum(
            TicketStatus,
            values_callable=lambda enum: [item.value for item in enum],
        ),
    )

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None


class TicketCreate(SQLModel):
    service_date: date
    service_time: time

    contractor: str
    client: str
    address: str

    description: str
    value: float
