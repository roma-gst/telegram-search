from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.record import Record


class RecordRepository:
    def __init__(self, session: Session):
        self.session = session

    def search(
        self,
        name: str | None = None,
        cidade: str | None = None,
        estado: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Record]:
        statement = select(Record)

        if name:
            statement = statement.where(Record.nome.ilike(f"%{name}%"))

        if cidade:
            statement = statement.where(Record.cidade.ilike(f"%{cidade}%"))

        if estado:
            statement = statement.where(Record.estado == estado.upper())

        statement = statement.offset(offset).limit(limit)

        return list(self.session.scalars(statement).all())