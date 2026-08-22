from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.record import Record


class RecordRepository:
    def __init__(self, session: Session):
        self.session = session

    def search_by_name(
        self,
        name: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Record]:
        statement = (
            select(Record)
            .where(Record.nome.ilike(f"%{name}%"))
            .offset(offset)
            .limit(limit)
        )

        return list(self.session.scalars(statement).all())