from pydantic import BaseModel

import database as db
from models.chamado import Ticket
from utils import get_current_datetime


class TicketService(BaseModel):
    @staticmethod
    def find_all() -> list[Ticket]:
        return db.find_all()

    @staticmethod
    def find_by_id(c_id):
        return db.find_by_id(c_id)

    @staticmethod
    def create(t: Ticket):
        date, time = get_current_datetime()
        t.service_date = date
        t.start_time = time

        db.create(t)

    @staticmethod
    def update(c_id: int, c: Ticket):
        return db.update(c_id, c)
