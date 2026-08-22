from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.config.settings import settings


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Olá! Bot funcionando."
    )


def create_bot() -> Application:
    if not settings.telegram_bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN não configurado.")

    application = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .build()
    )

    application.add_handler(CommandHandler("start", start))

    return application


if __name__ == "__main__":
    bot = create_bot()
    bot.run_polling()