<<<<<<< HEAD
from sqlmodel import SQLModel, create_engine, Session, select
=======
from sqlmodel import SQLModel, create_engine
>>>>>>> main

from models.ticket_model import Ticket


<<<<<<< HEAD
DATABASE_URL: str = "sqlite:///database.db"
=======
DATABASE_URL = "sqlite:///database.db"
>>>>>>> main

engine = create_engine(
    DATABASE_URL,
    echo=True,
)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


<<<<<<< HEAD
def get_session():
    with Session(engine) as session:
        yield session
=======
def verify_db_ddl() -> None:
    table = SQLModel.metadata.tables["ticket"]

    for column in table.columns:
        print(
            column.name,
            "| nullable:",
            column.nullable,
            "| primary_key:",
            column.primary_key,
            "| type:",
            column.type,
            "| default:",
            column.default,
        )
    return None
>>>>>>> main
