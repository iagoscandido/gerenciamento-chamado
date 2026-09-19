import sqlite3
from contextlib import contextmanager

from models.chamado import Ticket

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
        end_time TIME NOT NULL,

        address TEXT NOT NULL,
        client TEXT NOT NULL,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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


def find_by_id(t_id: str):
    with get_db() as conn:
        result = conn.execute(
            """
            SELECT *
            FROM tickets
            WHERE id = ?
            """,
            (t_id,),
        ).fetchone()

        return result


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
                address = ?
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
