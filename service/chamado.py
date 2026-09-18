from pydantic import BaseModel

from models.chamado import Chamado

import database as db


class ChamadoService(BaseModel):
    @staticmethod
    def find_all() -> list[Chamado]:
        return db.find_all()

    @staticmethod
    def find_by_id(c_id):
        return db.find_by_id(c_id)

    @staticmethod
    def create(c: Chamado) -> bool:
        result = db.create(c)
        if result is not None:
            return True
        return False

    @staticmethod
    def update(c_id: int, c: Chamado):
        return db.update(c_id, c)
