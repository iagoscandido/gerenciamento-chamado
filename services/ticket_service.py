from models.ticket_model import TicketUpdate
from datetime import UTC, datetime

from sqlalchemy import func
from sqlmodel import Session, select

from models.ticket_model import Ticket, TicketCreate, TicketStatus


class TicketService:
    def __init__(self, session: Session):
        self.session = session

    def start_travel(self, ticket_id: int) -> Ticket:
        ticket = self._get_ticket(ticket_id)

        if ticket.status != TicketStatus.SCHEDULED:
            raise ValueError(
                "Ticket cannot start travel from its current status")

        now = datetime.now(UTC)

        ticket.travel_start_time = now.time()
        ticket.status = TicketStatus.ON_TRAVEL
        ticket.updated_at = now

        self.session.commit()
        self.session.refresh(ticket)

        return ticket

    def cancel(self, ticket_id: int) -> Ticket:
        ticket = self._get_ticket(ticket_id)

        if ticket.status not in {
            TicketStatus.SCHEDULED,
            TicketStatus.ON_TRAVEL,
        }:
            raise ValueError(
                "Ticket cannot be canceled from its current status")

        now = datetime.now(UTC)

        ticket.status = TicketStatus.CANCELED
        ticket.updated_at = now

        self.session.commit()
        self.session.refresh(ticket)

        return ticket

    def start_service(self, ticket_id: int) -> Ticket:
        ticket = self._get_ticket(ticket_id)

        if ticket.status != TicketStatus.ON_TRAVEL:
            raise ValueError("Ticket cannot start service")

        now = datetime.now(UTC)

        ticket.service_start_time = now.time()
        ticket.status = TicketStatus.IN_PROGRESS
        ticket.updated_at = now

        self.session.commit()
        self.session.refresh(ticket)

        return ticket

    def finish_service(self, ticket_id: int) -> Ticket:
        ticket = self._get_ticket(ticket_id)

        if ticket.status != TicketStatus.IN_PROGRESS:
            raise ValueError("Ticket cannot finish service")

        now = datetime.now(UTC)

        ticket.service_finish_time = now.time()
        ticket.status = TicketStatus.FINISHED
        ticket.updated_at = now

        self.session.commit()
        self.session.refresh(ticket)

        return ticket

    def create(self, ticket: TicketCreate) -> Ticket:
        db_ticket = Ticket.model_validate(ticket)

        self.session.add(db_ticket)
        self.session.commit()
        self.session.refresh(db_ticket)

        return db_ticket

    def get_summary(self) -> dict[str, int]:
        total = self.session.exec(
            select(func.count()).select_from(Ticket)).one()

        scheduled = self.session.exec(
            select(func.count())
            .select_from(Ticket)
            .where(Ticket.status == TicketStatus.SCHEDULED)
        ).one()

        finished = self.session.exec(
            select(func.count())
            .select_from(Ticket)
            .where(Ticket.status == TicketStatus.FINISHED)
        ).one()

        return {
            "total": total,
            "scheduled": scheduled,
            "finished": finished,
        }

    def get_by_id(self, ticket_id: int) -> Ticket | None:
        return self.session.get(Ticket, ticket_id)

    def get_all(self) -> list[Ticket]:
        return self.session.exec(select(Ticket)).all()

    def update(self, ticket_id: int, ticket: TicketUpdate) -> Ticket | None:
        db_ticket = self.get_by_id(ticket_id)

        if db_ticket is None:
            return None

        ticket_data = ticket.model_dump(exclude_unset=True)

        db_ticket.sqlmodel_update(ticket_data)

        self.session.add(db_ticket)
        self.session.commit()
        self.session.refresh(db_ticket)

        return db_ticket

    def _get_ticket(self, ticket_id: int) -> Ticket:
        ticket = self.session.get(Ticket, ticket_id)

        if ticket is None:
            raise ValueError("Ticket not found")

        return ticket
