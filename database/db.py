import sqlite3
from contextlib import contextmanager

DB_NAME: str = "tickets.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
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
    ddl = """
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        
        service_date TEXT NOT NULL,
        contractor TEXT NOT NULL,
        value REAL NOT NULL,
        address TEXT NOT NULL,
        client TEXT NOT NULL,
        
        start_travel TEXT,

        start_time TEXT,

        protocol TEXT,
        end_time TEXT,

        status TEXT NOT NULL,
        
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT
    );
    """

    with get_db() as conn:
        conn.execute(ddl)
