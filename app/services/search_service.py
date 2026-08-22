from sqlalchemy.orm import Session

from app.models.record import Record
from app.repositories.record_repository import RecordRepository


class SearchService:
    def __init__(self, session: Session):
        self.repository = RecordRepository(session)

    def search(
        self,
        name: str | None = None,
        cidade: str | None = None,
        estado: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Record]:
        if not any([name, cidade, estado]):
            raise ValueError("Informe pelo menos um filtro.")

        if name and len(name.strip()) > 100:
            raise ValueError("A busca por nome é muito longa.")

        if cidade and len(cidade.strip()) > 100:
            raise ValueError("A busca por cidade é muito longa.")

        if estado and len(estado.strip()) != 2:
            raise ValueError("O estado deve ter 2 letras.")

        if limit < 1 or limit > 100:
            raise ValueError("O limite deve estar entre 1 e 100.")

        if offset < 0:
            raise ValueError("O offset não pode ser negativo.")

        return self.repository.search(
            name=name.strip() if name else None,
            cidade=cidade.strip() if cidade else None,
            estado=estado.strip() if estado else None,
            limit=limit,
            offset=offset,
        )