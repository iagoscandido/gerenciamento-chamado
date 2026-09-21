from datetime import datetime


def get_current_datetime() -> tuple[str, str]:
    """returns a tuple that contains date (%Y-%m-%d) and time (%H:%M)"""
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    hour_minute = now.strftime("%H:%M")
    return date, hour_minute


def solutec_info(
    nome: str,
    contratante: str,
    protocolo_chamado: str,
    cliente: str,
    data: str,
    hora_deslocamento: str,
    hora_inicio: str,
    hora_fim: str,
) -> str:

    return f"""
    Nome: {nome}
    Contratante: {contratante}
    N° Chamado: {protocolo_chamado}
    Cliente: {cliente}
    Data: {data}
    Deslocamento: {hora_deslocamento}
    Hora início: {hora_inicio}
    Hora finalizado: {hora_fim}
    """
