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
from app.models.record import Record
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
    records,
    search_text: str,
    offset: int,
    has_next: bool,
) -> InlineKeyboardMarkup:
    buttons = []

    for record in records:
        buttons.append(
            [
                InlineKeyboardButton(
                    f"Ver detalhes #{record.id}",
                    callback_data=f"detalhe:{record.id}",
                )
            ]
        )

    navigation = []

    if offset > 0:
        navigation.append(
            InlineKeyboardButton(
                "⬅️ Anterior",
                callback_data=f"buscar:{offset - PAGE_SIZE}:{search_text}",
            )
        )

    if has_next:
        navigation.append(
            InlineKeyboardButton(
                "Próxima ➡️",
                callback_data=f"buscar:{offset + PAGE_SIZE}:{search_text}",
            )
        )

    if navigation:
        buttons.append(navigation)

    return InlineKeyboardMarkup(buttons)


def parse_search(text: str) -> tuple[str, str | None, str | None]:
    parts = [part.strip() for part in text.split("|")]

    if len(parts) > 3:
        raise ValueError(
            "Formato inválido.\n"
            "Use: /buscar Nome | UF | Cidade"
        )

    name = parts[0]

    if not name:
        raise ValueError("Informe um nome.")

    estado = parts[1].upper() if len(parts) > 1 and parts[1] else None
    cidade = parts[2] if len(parts) > 2 and parts[2] else None

    if estado and len(estado) != 2:
        raise ValueError(
            "O estado deve ter 2 letras.\n"
            "Exemplo: /buscar Ana | SP"
        )

    return name, estado, cidade


def search_records(
    name: str,
    estado: str | None,
    cidade: str | None,
    offset: int,
):
    with Session(engine) as session:
        service = SearchService(session)

        records = service.search(
            name=name,
            estado=estado,
            cidade=cidade,
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
        "Use:\n"
        "/buscar Ana\n"
        "/buscar Ana | SP\n"
        "/buscar Ana | SP | São Paulo"
    )


async def buscar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    text = update.message.text or ""
    search_text = text.removeprefix("/buscar").strip()

    if not search_text:
        await update.message.reply_text(
            "Informe um nome.\n\n"
            "Exemplo:\n"
            "/buscar Ana\n"
            "/buscar Ana | SP\n"
            "/buscar Ana | SP | São Paulo"
        )
        return

    try:
        name, estado, cidade = parse_search(search_text)

        records, has_next = search_records(
            name=name,
            estado=estado,
            cidade=cidade,
            offset=0,
        )

    except ValueError as error:
        await update.message.reply_text(str(error))
        return

    if not records:
        await update.message.reply_text(
            f"Nenhum resultado encontrado para: {search_text}"
        )
        return

    await update.message.reply_text(
        format_results(records, search_text, 0),
        reply_markup=build_keyboard(
            records,
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

    try:
        name, estado, cidade = parse_search(search_text)

        records, has_next = search_records(
            name=name,
            estado=estado,
            cidade=cidade,
            offset=offset,
        )

    except ValueError:
        return

    if not records:
        return

    await query.edit_message_text(
        format_results(
            records=records,
            search_text=search_text,
            offset=offset,
        ),
        reply_markup=build_keyboard(
            records,
            search_text,
            offset,
            has_next,
        ),
    )


async def detail(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    await query.answer()

    _, record_id_text = query.data.split(":", 1)
    record_id = int(record_id_text)

    with Session(engine) as session:
        record = session.get(Record, record_id)

    if not record:
        await query.edit_message_text(
            "Registro não encontrado."
        )
        return

    text = (
        f"ID: {record.id}\n\n"
        f"Nome: {record.nome}\n"
        f"Email: {record.email}\n"
        f"Telefone: {record.telefone}\n"
        f"Cidade: {record.cidade}\n"
        f"Estado: {record.estado}\n"
        f"Data de nascimento: {record.data_nascimento}\n"
        f"Username: {record.username}\n"
        f"Empresa: {record.empresa}\n"
        f"Data de cadastro: {record.data_cadastro}"
    )

    await query.edit_message_text(text)


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

    application.add_handler(
        CallbackQueryHandler(
            detail,
            pattern=r"^detalhe:",
        )
    )

    return application


if __name__ == "__main__":
    bot = create_bot()
    bot.run_polling()