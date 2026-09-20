from datetime import date

from pydantic import BaseModel


class Ticket(BaseModel):
    id: int | None = None

    service_date: str
    start_time: str = ""
    end_time: str | None = None

    client: str = ""
    address: str = ""
