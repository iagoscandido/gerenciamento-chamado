from pydantic import BaseModel


class Ticket(BaseModel):
    service_date: str = ""
    start_time: str = ""
    end_time: str = ""

    client: str = ""

    address: str = ""
