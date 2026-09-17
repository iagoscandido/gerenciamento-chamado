from datetime import date, time

from pydantic import BaseModel


class Chamado(BaseModel):
    data_atendimento: str
    hora_inicio: str
    hora_fim: str

    valor: float
    despesas: float

    cliente: str
    contato: str

    localidade: str
    cliente_final: str

    escopo: str
    resumo_tecnico: str
