from models.ticket import Ticket, TicketStatus
from database.ticket_repository import TicketRepository
from utils import get_current_datetime

repository = TicketRepository()


class TicketService:
    @staticmethod
    def create(ticket: Ticket) -> Ticket:
        print("executou service")
        return repository.create(ticket)

    @staticmethod
    def start_travel(t_id: int) -> Ticket | None:
        ticket = get_ticket(t_id)

        if ticket.status != TicketStatus.OPEN:
            return None

        _, time = get_current_datetime()

        TicketRepository.start_travel(
            t_id,
            time,
        )

        return ticket

    @staticmethod
    def find_by_id(t_id: int) -> Ticket:
        ticket = get_ticket(t_id)

        return ticket

    @staticmethod
    def find_all() -> list[Ticket]:
        return repository.find_all()


def get_ticket(t_id: int) -> Ticket:
    """make a select query and returns the ticket, if no found, raise exeption"""
    ticket = repository.find_by_id(t_id)

    if ticket is None:
        raise Exception(
            f"get_ticket() - ticket for the id:{t_id} does not exists or it was not found"
        )

    return ticket
