from datetime import UTC, date, datetime, time
from enum import StrEnum

from sqlmodel import Field, SQLModel


class TicketStatus(StrEnum):
    SCHEDULED = "scheduled"
    ON_TRAVEL = "on_travel"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    CANCELED = "canceled"


# 1. identificação
# 2. agendamento
# 3. envolvidos/local
# 4. serviço/valor
# 5. execução
# 6. estado
# 7. auditoria


class Ticket(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    service_date: date
    service_time: time

    contractor: str
    client: str
    address: str

    scope: str
    value: float

    travel_start_time: time | None = None
    service_start_time: time | None = None
    service_finish_time: time | None = None

    technical_summary: str | None = None

    status: TicketStatus = Field(default=TicketStatus.SCHEDULED)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    updated_at: datetime | None = None
