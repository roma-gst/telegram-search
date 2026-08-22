import argparse
from datetime import datetime

from faker import Faker
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.database.session import engine
from app.models.record import Record


fake = Faker("pt_BR")


def generate_records(quantity: int, reset: bool = False) -> None:
    with Session(engine) as session:
        if reset:
            session.execute(delete(Record))
            session.commit()
            print("Registros existentes removidos.")

        records = []

        for _ in range(quantity):
            record = Record(
                nome=fake.name(),
                email=f"{fake.uuid4()}@example.com",
                telefone=f"+55 11 9{fake.msisdn()[-8:]}",
                cidade=fake.city(),
                estado=fake.estado_sigla(),
                data_nascimento=fake.date_of_birth(
                    minimum_age=18,
                    maximum_age=80,
                ),
                username=f"user_{fake.uuid4().replace('-', '')[:12]}",
                empresa=fake.company(),
                data_cadastro=datetime.now(),
            )

            records.append(record)

        session.add_all(records)
        session.commit()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera dados sintéticos para o banco."
    )

    parser.add_argument(
        "--records",
        type=int,
        required=True,
        help="Quantidade de registros a gerar.",
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="Remove os registros existentes antes de gerar novos.",
    )

    args = parser.parse_args()

    if args.records <= 0:
        raise ValueError("A quantidade de registros deve ser maior que zero.")

    print(f"Gerando {args.records} registros...")

    generate_records(args.records, args.reset)

    print("Dados gerados com sucesso.")


if __name__ == "__main__":
    main()