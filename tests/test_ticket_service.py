from datetime import date, time

from pytest import raises
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from models.ticket_model import Ticket, TicketCreate, TicketStatus
from services.ticket_service import TicketService


def test_start_travel():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        ticket = Ticket(
            service_date=date(2026, 9, 25),
            service_time=time(9, 0),
            contractor="Empresa ABC",
            client="Cliente XYZ",
            address="Rua Exemplo, 100",
            scope="Manutenção preventiva",
            value=500.0,
        )

        session.add(ticket)
        session.commit()
        session.refresh(ticket)

        assert ticket.id is not None

        service = TicketService(session)

        updated_ticket = service.start_travel(ticket.id)

        assert updated_ticket.status == TicketStatus.ON_TRAVEL
        assert updated_ticket.travel_start_time is not None
        assert updated_ticket.updated_at is not None


def test_start_travel_when_already_on_travel():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        ticket = Ticket(
            service_date=date(2026, 9, 25),
            service_time=time(9, 0),
            contractor="Empresa ABC",
            client="Cliente XYZ",
            address="Rua Exemplo, 100",
            scope="Manutenção preventiva",
            value=500.0,
        )

        ticket.status = TicketStatus.ON_TRAVEL

        session.add(ticket)
        session.commit()
        session.refresh(ticket)

        assert ticket.id is not None

        service = TicketService(session)

        with raises(ValueError):
            service.start_travel(ticket.id)


def test_cancel_scheduled_ticket():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        ticket = Ticket(
            service_date=date(2026, 9, 25),
            service_time=time(9, 0),
            contractor="Empresa ABC",
            client="Cliente XYZ",
            address="Rua Exemplo, 100",
            scope="Manutenção preventiva",
            value=500.0,
        )

        session.add(ticket)
        session.commit()
        session.refresh(ticket)

        assert ticket.id is not None

        service = TicketService(session)

        updated_ticket = service.cancel(ticket.id)

        assert updated_ticket.status == TicketStatus.CANCELED
        assert updated_ticket.updated_at is not None


def test_cancel_ticket_on_travel():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        ticket = Ticket(
            service_date=date(2026, 9, 25),
            service_time=time(9, 0),
            contractor="Empresa ABC",
            client="Cliente XYZ",
            address="Rua Exemplo, 100",
            scope="Manutenção preventiva",
            value=500.0,
        )

        session.add(ticket)
        session.commit()
        session.refresh(ticket)

        assert ticket.id is not None

        service = TicketService(session)

        service.start_travel(ticket.id)
        updated_ticket = service.cancel(ticket.id)

        assert updated_ticket.status == TicketStatus.CANCELED
        assert updated_ticket.travel_start_time is not None
        assert updated_ticket.updated_at is not None


def test_cannot_cancel_ticket_in_progress():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        ticket = Ticket(
            service_date=date(2026, 9, 25),
            service_time=time(9, 0),
            contractor="Empresa ABC",
            client="Cliente XYZ",
            address="Rua Exemplo, 100",
            scope="Manutenção preventiva",
            value=500.0,
            status=TicketStatus.IN_PROGRESS,
        )

        session.add(ticket)
        session.commit()
        session.refresh(ticket)

        assert ticket.id is not None

        service = TicketService(session)

        with raises(ValueError):
            service.cancel(ticket.id)

        session.refresh(ticket)

        assert ticket.status == TicketStatus.IN_PROGRESS


def test_cannot_cancel_finished_ticket():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        ticket = Ticket(
            service_date=date(2026, 9, 25),
            service_time=time(9, 0),
            contractor="Empresa ABC",
            client="Cliente XYZ",
            address="Rua Exemplo, 100",
            scope="Manutenção preventiva",
            value=500.0,
            status=TicketStatus.FINISHED,
        )

        session.add(ticket)
        session.commit()
        session.refresh(ticket)

        assert ticket.id is not None

        service = TicketService(session)

        with raises(ValueError):
            service.cancel(ticket.id)

        session.refresh(ticket)

        assert ticket.status == TicketStatus.FINISHED


def test_cannot_cancel_canceled_ticket():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        ticket = Ticket(
            service_date=date(2026, 9, 25),
            service_time=time(9, 0),
            contractor="Empresa ABC",
            client="Cliente XYZ",
            address="Rua Exemplo, 100",
            scope="Manutenção preventiva",
            value=500.0,
            status=TicketStatus.CANCELED,
        )

        session.add(ticket)
        session.commit()
        session.refresh(ticket)

        assert ticket.id is not None

        service = TicketService(session)

        with raises(ValueError):
            service.cancel(ticket.id)

        session.refresh(ticket)

        assert ticket.status == TicketStatus.CANCELED


def test_start_service():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        ticket = Ticket(
            service_date=date.today(),
            service_time=time(10, 0),
            contractor="Empresa Teste",
            client="Cliente Teste",
            address="Rua Teste, 123",
            scope="Manutenção",
            value=100.0,
        )

        session.add(ticket)
        session.commit()
        session.refresh(ticket)

        service = TicketService(session)

        service.start_travel(ticket.id)

        updated_ticket = service.start_service(ticket.id)

        assert updated_ticket.status == TicketStatus.IN_PROGRESS
        assert updated_ticket.service_start_time is not None
        assert updated_ticket.travel_start_time is not None
        assert updated_ticket.updated_at is not None


def test_start_service_when_scheduled():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        ticket = Ticket(
            service_date=date.today(),
            service_time=time(10, 0),
            contractor="Empresa Teste",
            client="Cliente Teste",
            address="Rua Teste, 123",
            scope="Manutenção",
            value=100.0,
        )

        session.add(ticket)
        session.commit()
        session.refresh(ticket)

        service = TicketService(session)

        with raises(ValueError):
            service.start_service(ticket.id)

        session.refresh(ticket)

        assert ticket.status == TicketStatus.SCHEDULED


def test_finish_service():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        ticket = Ticket(
            service_date=date.today(),
            service_time=time(10, 0),
            contractor="Empresa Teste",
            client="Cliente Teste",
            address="Rua Teste, 123",
            scope="Manutenção",
            value=100.0,
        )

        session.add(ticket)
        session.commit()
        session.refresh(ticket)

        service = TicketService(session)

        service.start_travel(ticket.id)
        service.start_service(ticket.id)

        updated_ticket = service.finish_service(ticket.id)

        assert updated_ticket.status == TicketStatus.FINISHED
        assert updated_ticket.travel_start_time is not None
        assert updated_ticket.service_start_time is not None
        assert updated_ticket.service_finish_time is not None
        assert updated_ticket.updated_at is not None


def test_finish_service_when_scheduled():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        ticket = Ticket(
            service_date=date.today(),
            service_time=time(10, 0),
            contractor="Empresa Teste",
            client="Cliente Teste",
            address="Rua Teste, 123",
            scope="Manutenção",
            value=100.0,
        )

        session.add(ticket)
        session.commit()
        session.refresh(ticket)

        service = TicketService(session)

        with raises(ValueError):
            service.finish_service(ticket.id)

        session.refresh(ticket)

        assert ticket.status == TicketStatus.SCHEDULED


def test_create_ticket():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        ticket = TicketCreate(
            service_date=date.today(),
            service_time=time(10, 0),
            contractor="Empresa Teste",
            client="Cliente Teste",
            address="Rua Teste, 123",
            scope="Manutenção",
            value=100.0,
        )

        service = TicketService(session)

        created_ticket = service.create(ticket)

        assert created_ticket.id is not None
        assert created_ticket.status == TicketStatus.SCHEDULED
        assert created_ticket.contractor == "Empresa Teste"
        assert created_ticket.client == "Cliente Teste"
        assert created_ticket.address == "Rua Teste, 123"
