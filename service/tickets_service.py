from pydantic import BaseModel

import database as db
from models.ticket_model import Ticket


class TicketService(BaseModel):
    @staticmethod
    def find_all() -> list[Ticket]:
        return db.find_all()

    @staticmethod
    def find_by_id(t_id: int) -> Ticket | None:
        return db.find_by_id(str(t_id))

    @staticmethod
    def create(t: Ticket):

        return db.create(t)

    @staticmethod
    def update(t_id: int, t: Ticket):
        return db.update(t_id, t)

    @staticmethod
    def find_active():
        return db.find_active()
