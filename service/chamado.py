from pydantic import BaseModel

from models.chamado import Chamado

import database as db


class ChamadoService(BaseModel):

    @staticmethod
    def find_all():
        return db.find_all()

    @staticmethod
    def create(c: Chamado):
        return db.create(c)
