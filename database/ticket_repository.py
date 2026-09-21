from database.db import get_db
from models.ticket import Ticket, TicketStatus


class TicketRepository:
    @staticmethod
    def create(t: Ticket) -> Ticket:
        with get_db() as conn:

            cursor = conn.execute(
                """
                INSERT INTO tickets (
                    service_date,
                    client,
                    address,
                    value,
                    contractor,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    t.service_date,
                    t.client,
                    t.address,
                    t.value,
                    t.contractor,
                    t.status.value,
                ),
            )

            ticket_id = cursor.lastrowid

            ticket = conn.execute(
                """
                SELECT *
                FROM tickets
                WHERE id = ?
            """,
                (ticket_id,),
            ).fetchone()

            if ticket is None:
                raise RuntimeError(
                    "Ticket was created but could not be retrieved")

            return Ticket(
                id=ticket["id"],
                protocol=ticket["protocol"],
                service_date=ticket["service_date"],
                start_travel=ticket["start_travel"],
                start_time=ticket["start_time"],
                end_time=ticket["end_time"],
                client=ticket["client"],
                address=ticket["address"],
                value=ticket["value"],
                contractor=ticket["contractor"],
                status=ticket["status"],
                created_at=ticket["created_at"],
                updated_at=ticket["updated_at"],
            )

    @staticmethod
    def find_by_id(ticket_id: int) -> Ticket | None:
        with get_db() as conn:

            ticket = conn.execute(
                """
                SELECT *
                FROM tickets
                WHERE id = ?
                """,
                (ticket_id,),
            ).fetchone()

            if ticket is None:
                return None

            return Ticket(
                id=ticket["id"],
                protocol=ticket["protocol"],
                service_date=ticket["service_date"],
                start_travel=ticket["start_travel"],
                start_time=ticket["start_time"],
                end_time=ticket["end_time"],
                client=ticket["client"],
                address=ticket["address"],
                value=ticket["value"],
                contractor=ticket["contractor"],
                status=ticket["status"],
                created_at=ticket["created_at"],
                updated_at=ticket["updated_at"],
            )

    @staticmethod
    def start_travel(ticket_id: int, start_travel: str) -> Ticket | None:
        with get_db() as conn:
            cursor = conn.execute(
                """
                UPDATE tickets
                SET
                    start_travel = ?,
                    status = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    start_travel,
                    TicketStatus.ON_TRAVEL.value,
                    ticket_id,
                ),
            )

            if cursor.rowcount == 0:
                return None

            ticket = conn.execute(
                """
                SELECT *
                FROM tickets
                WHERE id = ?
                """,
                (ticket_id,),
            ).fetchone()

        if ticket is None:
            return None

        return Ticket(**dict(ticket))

    @staticmethod
    def find_all() -> list[Ticket]:
        with get_db() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM tickets
                ORDER BY id DESC
                """
            ).fetchall()

        return [Ticket(**dict(row)) for row in rows]
