# Telegram Search

Projeto de busca de registros usando PostgreSQL, FastAPI e Telegram Bot.

## Tecnologias

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Psycopg
- Pydantic Settings
- python-telegram-bot
- Faker

## Estrutura

```text
telegram/
├── app/
│   ├── api/
│   ├── bot/
│   │   └── main.py
│   ├── config/
│   ├── database/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   └── main.py
├── scripts/
│   ├── generate_data.py
│   ├── start_api.ps1
│   └── start_bot.ps1
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md