from app.database.base import Base
from app.database.session import engine
from app.models.record import Record


def init_database() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_database()
    print("Banco inicializado com sucesso.")