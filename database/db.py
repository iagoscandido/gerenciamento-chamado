from sqlmodel import SQLModel, create_engine, Session, select

from models.ticket_model import Ticket


DATABASE_URL: str = "sqlite:///database.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,
)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
