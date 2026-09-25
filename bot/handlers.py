from telegram.ext import ConversationHandler
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes


SERVICE_DATE = 0
SERVICE_TIME = 1
CONTRACTOR = 2
CLIENT = 3


async def start_ticket(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    print("DEBUG: start_ticket foi chamado")
    print(f"DEBUG: mensagem = {update.message.text}")

    await update.message.reply_text(
        "Informe a data do atendimento no formato DD/MM/AAAA:"
    )

    print(f"DEBUG: retornando estado {SERVICE_DATE}")

    return SERVICE_DATE


async def receive_service_date(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    print("DEBUG: receive_service_date foi chamado")
    print(f"DEBUG: mensagem = {update.message.text}")

    text = update.message.text.strip()

    try:
        service_date = datetime.strptime(
            text,
            "%d/%m/%Y",
        ).date()

        print(f"DEBUG: data convertida = {service_date}")

    except ValueError:
        print("DEBUG: data inválida")

        await update.message.reply_text(
            "Data inválida. Informe no formato DD/MM/AAAA:"
        )

        return SERVICE_DATE

    context.user_data["service_date"] = service_date

    print(
        "DEBUG: service_date armazenada =",
        context.user_data["service_date"],
    )

    await update.message.reply_text(
        "Informe o horário do atendimento no formato HH:MM:"
    )

    print(f"DEBUG: retornando estado {SERVICE_TIME}")

    return SERVICE_TIME


async def receive_service_time(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    print("DEBUG: receive_service_time foi chamado")
    print(f"DEBUG: mensagem = {update.message.text}")

    text = update.message.text.strip()

    try:
        service_time = datetime.strptime(
            text,
            "%H:%M",
        ).time()

        print(f"DEBUG: horário convertido = {service_time}")

    except ValueError:
        print("DEBUG: horário inválido")

        await update.message.reply_text(
            "Horário inválido. Informe no formato HH:MM:"
        )

        return SERVICE_TIME

    context.user_data["service_time"] = service_time

    print(
        "DEBUG: service_time armazenado =",
        context.user_data["service_time"],
    )

    await update.message.reply_text(
        "Informe o contratante:"
    )

    print(f"DEBUG: retornando estado {CONTRACTOR}")

    print("DEBUG: encerrando ConversationHandler")
    return CONTRACTOR


async def receive_contractor(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    contractor = update.message.text.strip()

    context.user_data["contractor"] = contractor

    await update.message.reply_text(
        "Contratante registrado."
    )

    return CLIENT


async def receive_client(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    client = update.message.text.strip()

    context.user_data["client"] = client

    await update.message.reply_text(
        "Cliente registrado."
    )

    return ConversationHandler.END
