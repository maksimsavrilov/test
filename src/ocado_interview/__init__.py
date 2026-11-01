import argparse
import os

from sqlalchemy import create_engine

from ocado_interview.databaseloader import DatabaseLoader
from ocado_interview.filereader import FileReader


def main() -> None:
    parser = argparse.ArgumentParser(description='Process some orders.')
    parser.add_argument('--filename', help='Path to the file to process')
    args = parser.parse_args()

    if args.filename is None:
        raise ValueError("Please provide a filename using the --filename argument.")
    print(f"Processing file: {args.filename}")
    my_reader = FileReader(args.filename)
    orders, dlq = my_reader.get_orders()
    db_dsn = os.getenv("DB_DSN", "postgresql://ocado:ocado-dev@localhost:5432/orders")
    engine = create_engine(db_dsn, echo=True)
    my_loader = DatabaseLoader(engine)
    my_loader.insert_orders(orders)
    print(f"Inserted {len(orders)} orders into the database.")
    print(f"Skipped {len(dlq)} invalid orders (DLQ).")

if __name__ == "__main__":
    main()
