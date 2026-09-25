from os import getenv

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sistema de Chamados")


def main():
    token = getenv("TELEGRAM_BOT_TOKEN")

    if token is None:
        raise ValueError("TELEGRAM_BOT_TOKEN must be defined.")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))

    application.run_polling()


if __name__ == "__main__":
    main()
