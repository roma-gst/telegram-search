from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Record(Base):
    __tablename__ = "records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    telefone: Mapped[str] = mapped_column(String(30), nullable=False)
    cidade: Mapped[str] = mapped_column(String(100), nullable=False)
    estado: Mapped[str] = mapped_column(String(2), nullable=False)
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    empresa: Mapped[str] = mapped_column(String(150), nullable=False)
    data_cadastro: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )