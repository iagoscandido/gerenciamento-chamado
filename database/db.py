from sqlmodel import SQLModel, create_engine

from models.ticket_model import Ticket


DATABASE_URL = "sqlite:///database.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,
)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


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
