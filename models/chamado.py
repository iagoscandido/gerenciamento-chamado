from pydantic import BaseModel


class Chamado(BaseModel):
    data_atendimento: str = ""
    hora_inicio: str = ""
    hora_fim: str = ""

    valor: float = 0.0
    despesas: float = 0.0

    cliente: str = ""
    contato: str = ""

    localidade: str = ""
    cliente_final: str = ""

    escopo: str = ""
    resumo_tecnico: str = ""
