from pydantic import BaseModel

from models.chamado import Chamado

import database as db


class ChamadoService(BaseModel):
    @staticmethod
    def find_all():
        return db.find_all()

    @staticmethod
    def find_by_id(c_id):
        return db.find_by_id(c_id)

    @staticmethod
    def create(c: Chamado):
        return db.create(c)
