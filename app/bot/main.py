from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from sqlalchemy.orm import Session

from app.config.settings import settings
from app.database.session import engine
from app.services.search_service import SearchService


PAGE_SIZE = 10


def format_results(
    records,
    search_text: str,
    offset: int,
) -> str:
    page = (offset // PAGE_SIZE) + 1

    lines = [
        f"Resultados para: {search_text}",
        f"Página {page}",
        "",
    ]

    for record in records:
        lines.append(
            f"ID: {record.id}\n"
            f"Nome: {record.nome}\n"
            f"Cidade: {record.cidade} - {record.estado}\n"
            f"Username: {record.username}\n"
        )

    return "\n".join(lines)


def build_keyboard(
    search_text: str,
    offset: int,
    has_next: bool,
) -> InlineKeyboardMarkup:
    buttons = []

    if offset > 0:
        buttons.append(
            InlineKeyboardButton(
                "⬅️ Anterior",
                callback_data=f"buscar:{offset - PAGE_SIZE}:{search_text}",
            )
        )

    if has_next:
        buttons.append(
            InlineKeyboardButton(
                "Próxima ➡️",
                callback_data=f"buscar:{offset + PAGE_SIZE}:{search_text}",
            )
        )

    return InlineKeyboardMarkup([buttons]) if buttons else InlineKeyboardMarkup([])


def search_records(
    name: str,
    estado: str | None,
    offset: int,
):
    with Session(engine) as session:
        service = SearchService(session)

        records = service.search(
            name=name,
            estado=estado,
            limit=PAGE_SIZE + 1,
            offset=offset,
        )

    has_next = len(records) > PAGE_SIZE

    return records[:PAGE_SIZE], has_next


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await update.message.reply_text(
        "Olá! Bot funcionando.\n\n"
        "Use /buscar seguido de um nome.\n"
        "Exemplo: /buscar Ana\n"
        "Com estado: /buscar Ana SP"
    )


async def buscar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not context.args:
        await update.message.reply_text(
            "Informe um nome.\n"
            "Exemplo: /buscar Ana\n"
            "Com estado: /buscar Ana SP"
        )
        return

    args = context.args

    estado = None

    if len(args) >= 2 and len(args[-1]) == 2:
        estado = args[-1].upper()
        name = " ".join(args[:-1])
    else:
        name = " ".join(args)

    name = name.strip()

    try:
        records, has_next = search_records(
            name=name,
            estado=estado,
            offset=0,
        )
    except ValueError as error:
        await update.message.reply_text(str(error))
        return

    if not records:
        await update.message.reply_text(
            f"Nenhum resultado encontrado para: {' '.join(args)}"
        )
        return

    search_text = " ".join(args)

    await update.message.reply_text(
        format_results(records, search_text, 0),
        reply_markup=build_keyboard(
            search_text,
            0,
            has_next,
        ),
    )


async def pagination(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    await query.answer()

    _, offset_text, search_text = query.data.split(":", 2)
    offset = int(offset_text)

    args = search_text.split()

    estado = None

    if len(args) >= 2 and len(args[-1]) == 2:
        estado = args[-1].upper()
        name = " ".join(args[:-1])
    else:
        name = search_text

    records, has_next = search_records(
        name=name,
        estado=estado,
        offset=offset,
    )

    if not records:
        return

    await query.edit_message_text(
        format_results(records, search_text, offset),
        reply_markup=build_keyboard(
            search_text,
            offset,
            has_next,
        ),
    )


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

    application.add_handler(
        CallbackQueryHandler(
            pagination,
            pattern=r"^buscar:",
        )
    )

    return application


if __name__ == "__main__":
    bot = create_bot()
    bot.run_polling()