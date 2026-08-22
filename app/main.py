from fastapi import FastAPI, Query
from sqlalchemy.orm import Session

from app.database.session import engine
from app.services.search_service import SearchService


app = FastAPI(title="Telegram Search")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/records")
def search_records(
    name: str | None = Query(default=None),
    cidade: str | None = Query(default=None),
    estado: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    with Session(engine) as session:
        service = SearchService(session)

        records = service.search(
            name=name,
            cidade=cidade,
            estado=estado,
            limit=limit,
            offset=offset,
        )

        return [
            {
                "id": record.id,
                "nome": record.nome,
                "email": record.email,
                "telefone": record.telefone,
                "cidade": record.cidade,
                "estado": record.estado,
                "data_nascimento": record.data_nascimento,
                "username": record.username,
                "empresa": record.empresa,
                "data_cadastro": record.data_cadastro,
            }
            for record in records
        ]