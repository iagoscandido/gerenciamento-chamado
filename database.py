import sqlite3
from contextlib import contextmanager

from models.chamado import Chamado

DB_NAME = "chamados.db"


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
    CREATE TABLE IF NOT EXISTS chamados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        data_atendimento DATE NOT NULL,
        hora_inicio TIME NOT NULL,
        hora_fim TIME NOT NULL,

        valor REAL NOT NULL DEFAULT 0.0,
        despesas REAL NOT NULL DEFAULT 0.0,

        localidade TEXT NOT NULL,
        contato TEXT NOT NULL,

        cliente_final TEXT NOT NULL,
        cliente TEXT NOT NULL,

        escopo TEXT NOT NULL,
        resumo_tecnico TEXT NOT NULL,

        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    with get_db() as conn:
        conn.execute(ddl)


def find_all():
    with get_db() as conn:
        result = conn.execute("""
        SELECT * FROM chamados
        ORDER BY criado_em DESC
    """).fetchall()
    return result


def find_by_id(c_id: str):
    with get_db() as conn:
        result = conn.execute(
            """
            SELECT *
            FROM chamados
            WHERE id = ?
            """,
            (c_id,),
        ).fetchone()

        return result


def create(
    c: Chamado
):
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO chamados (
                data_atendimento,
                hora_inicio,
                hora_fim,
                valor,
                despesas,
                localidade,
                contato,
                cliente_final,
                cliente,
                escopo,
                resumo_tecnico
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                c.data_atendimento,
                c.hora_inicio,
                c.hora_fim,
                c.valor,
                c.despesas,
                c.localidade,
                c.contato,
                c.cliente_final,
                c.cliente,
                c.escopo,
                c.resumo_tecnico,
            ),
        )

        return cursor.lastrowid


def update(
    c_id: int,
    c: Chamado
):
    with get_db() as conn:
        cursor = conn.execute(
            """
            UPDATE chamados
            SET
                data_atendimento = ?,
                hora_inicio = ?,
                hora_fim = ?,
                valor = ?,
                despesas = ?,
                localidade = ?,
                contato = ?,
                cliente_final = ?,
                cliente = ?,
                escopo = ?,
                resumo_tecnico = ?
            WHERE id = ?
            """,
            (
                c.data_atendimento,
                c.hora_inicio,
                c.hora_fim,
                c.valor,
                c.despesas,
                c.localidade,
                c.contato,
                c.cliente_final,
                c.cliente,
                c.escopo,
                c.resumo_tecnico,
                c_id
            ),
        )

        return cursor.rowcount


def delete(c_id: int):
    with get_db() as conn:
        cursor = conn.execute(
            """
            DELETE FROM chamados
            WHERE id = ?
            """,
            (c_id,),
        )

        return cursor.rowcount
