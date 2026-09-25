from bot.handlers import receive_client
from bot.handlers import CLIENT
from bot.handlers import CONTRACTOR
from bot.handlers import receive_contractor
from bot.handlers import receive_service_time
from os import getenv

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.handlers import (
    SERVICE_DATE,
    SERVICE_TIME,
    receive_service_date,
    start_ticket,
)


load_dotenv()


async def start(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sistema de Chamados")


def main():
    print("DEBUG: iniciando bot")
    token = getenv("TELEGRAM_BOT_TOKEN")

    if token is None:
        raise ValueError("TELEGRAM_BOT_TOKEN must be defined.")

    print("DEBUG: Application criada")

    application = Application.builder().token(token).build()

    ticket_conversation = ConversationHandler(
        entry_points=[
            CommandHandler("novo", start_ticket),
        ],
        states={
            SERVICE_DATE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_service_date,
                ),
            ],
            SERVICE_TIME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_service_time,
                ),
            ],
            CONTRACTOR: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_contractor,
                ),
            ],
            CLIENT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receive_client,
                ),
            ],
        },
        fallbacks=[],
    )

    print("DEBUG: ConversationHandler criado")

    application.add_handler(CommandHandler("start", start))
    application.add_handler(ticket_conversation)

    print("DEBUG: handlers registrados")
    print("DEBUG: iniciando polling")

    application.run_polling()


if __name__ == "__main__":
    main()
