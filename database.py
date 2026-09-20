import sqlite3
from contextlib import contextmanager

from models.ticket_model import Ticket

DB_NAME = "tickets.db"


def get_connection():
    """Retorna uma conexão configurada com row_factory para acesso por chave."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    """Context manager para garantir commit/rollback e fechamento automático."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Cria a tabela de chamados com os campos do escopo."""
    ddl = """
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        service_date DATE NOT NULL,
        start_time TIME NOT NULL,
        end_time TIME,

        address TEXT NOT NULL,
        client TEXT NOT NULL,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    );
    """
    with get_db() as conn:
        conn.execute(ddl)


def find_all():
    with get_db() as conn:
        result = conn.execute("""
        SELECT * FROM tickets
        ORDER BY created_at DESC
    """).fetchall()
    return result


def find_by_id(t_id: str) -> Ticket | None:
    with get_db() as conn:
        ticket = conn.execute(
            """
            SELECT *
            FROM tickets
            WHERE id = ?
            """,
            (t_id,),
        ).fetchone()

        return Ticket(
            id=ticket["id"],
            service_date=ticket["service_date"],
            start_time=ticket["start_time"],
            end_time=ticket["end_time"],
            address=ticket["address"],
            client=ticket["client"],
        )


def create(ticket: Ticket):

    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO tickets (
                service_date,
                start_time,
                end_time,
                address,
                client
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                ticket.service_date,
                ticket.start_time,
                ticket.end_time,
                ticket.address,
                ticket.client,
            ),
        )

        return cursor.lastrowid


def update(t_id: int, t: Ticket):
    with get_db() as conn:
        cursor = conn.execute(
            """
            UPDATE tickets
            SET
                service_date = ?,
                start_time = ?,
                end_time = ?,
                client = ?,
                address = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                t.service_date,
                t.start_time,
                t.end_time,
                t.client,
                t.address,
                t_id,
            ),
        )

        return cursor.rowcount


def delete(t_id: int):
    with get_db() as conn:
        cursor = conn.execute(
            """
            DELETE FROM tickets
            WHERE id = ?
            """,
            (t_id,),
        )

        return cursor.rowcount


def find_active() -> Ticket | None:
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM tickets
            WHERE end_time IS NULL
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()

        if row is None:
            return None

        return Ticket(
            id=row["id"],
            service_date=row["service_date"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            address=row["address"],
            client=row["client"],
        )
