from collections.abc import Sequence
from models.ticket_model import TicketFinish
from datetime import UTC, datetime

from sqlalchemy import func
from sqlmodel import Session, select

from models.ticket_model import Ticket, TicketCreate, TicketStatus, TicketUpdate


class TicketService:
    def __init__(self, session: Session):
        self.session = session

    def start_travel(self, ticket_id: int) -> Ticket:
        ticket = self._get_ticket(ticket_id)

        now = datetime.now(UTC)

        ticket.travel_start_time = now.time()
        ticket.status = TicketStatus.ON_TRAVEL
        ticket.updated_at = now

        self.session.commit()
        self.session.refresh(ticket)

        return ticket

    def cancel_service(self, ticket_id: int) -> Ticket:
        ticket = self._get_ticket(ticket_id)

        now = datetime.now(UTC)

        ticket.status = TicketStatus.CANCELED
        ticket.updated_at = now

        self.session.commit()
        self.session.refresh(ticket)

        return ticket

    def start_service(self, ticket_id: int) -> Ticket:
        ticket = self._get_ticket(ticket_id)

        now = datetime.now(UTC)

        ticket.service_start_time = now.time()
        ticket.status = TicketStatus.IN_PROGRESS
        ticket.updated_at = now

        self.session.commit()
        self.session.refresh(ticket)

        return ticket

    def finish_service(self, ticket_id: int, ticket: TicketFinish) -> Ticket:
        ticket_db = self._get_ticket(ticket_id)

        now = datetime.now(UTC)

        ticket_db.technical_summary = ticket.technical_summary
        ticket_db.service_finish_time = now.time()
        ticket_db.status = TicketStatus.FINISHED
        ticket_db.updated_at = now

        self.session.commit()
        self.session.refresh(ticket_db)

        return ticket_db

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

    def get_all(self) -> Sequence[Ticket]:
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

    def delete(self, ticket_id: int) -> bool:
        ticket = self.get_by_id(ticket_id)

        if ticket is None:
            return False

        self.session.delete(ticket)
        self.session.commit()

        return True

    def _get_ticket(self, ticket_id: int) -> Ticket:
        """
        Try to find and return a ticket by its id.
        if the given ticket does not exists, it raise an exception
        """
        ticket = self.session.get(Ticket, ticket_id)

        if ticket is None:
            raise ValueError("Ticket not found")

        return ticket
