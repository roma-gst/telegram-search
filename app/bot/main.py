from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from sqlalchemy.orm import Session

from app.config.settings import settings
from app.database.session import engine
from app.services.search_service import SearchService


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await update.message.reply_text(
        "Olá! Bot funcionando.\n\n"
        "Use /buscar seguido de um nome.\n"
        "Exemplo: /buscar Ana"
    )


async def buscar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not context.args:
        await update.message.reply_text(
            "Informe um nome.\n"
            "Exemplo: /buscar Ana"
        )
        return

    name = " ".join(context.args)

    with Session(engine) as session:
        service = SearchService(session)
        records = service.search(
            name=name,
            limit=10,
        )

    if not records:
        await update.message.reply_text(
            f"Nenhum resultado encontrado para: {name}"
        )
        return

    lines = [f"Resultados para: {name}\n"]

    for record in records:
        lines.append(
            f"ID: {record.id}\n"
            f"Nome: {record.nome}\n"
            f"Cidade: {record.cidade} - {record.estado}\n"
            f"Username: {record.username}\n"
        )

    await update.message.reply_text("\n".join(lines))


def create_bot() -> Application:
    if not settings.telegram_bot_token:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN não configurado."
        )

    application = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("buscar", buscar)
    )

    return application


if __name__ == "__main__":
    bot = create_bot()
    bot.run_polling()