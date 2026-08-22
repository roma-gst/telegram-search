from sqlalchemy.orm import Session

from app.models.record import Record
from app.repositories.record_repository import RecordRepository


class SearchService:
    def __init__(self, session: Session):
        self.repository = RecordRepository(session)

    def search_by_name(
        self,
        name: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Record]:
        name = name.strip()

        if not name:
            raise ValueError("O nome da busca não pode estar vazio.")

        if len(name) > 100:
            raise ValueError("A busca é muito longa.")

        if limit < 1 or limit > 100:
            raise ValueError("O limite deve estar entre 1 e 100.")

        if offset < 0:
            raise ValueError("O offset não pode ser negativo.")

        return self.repository.search_by_name(
            name=name,
            limit=limit,
            offset=offset,
        )