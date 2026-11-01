import argparse

from sqlalchemy import create_engine

from src.ocado_interview.databaseloader import DatabaseLoader
from src.ocado_interview.filereader import FileReader


def main() -> None:
    parser = argparse.ArgumentParser(description='Process some orders.')
    parser.add_argument('--filename', help='Path to the file to process')
    args = parser.parse_args()

    if args.filename is None:
        raise ValueError("Please provide a filename using the --filename argument.")
    print(f"Processing file: {args.filename}")
    my_reader = FileReader(args.filename)
    orders, dlq = my_reader.get_orders()
    engine = create_engine('postgresql://ocado:ocado-dev@localhost:5432/orders', echo=True)
    my_loader = DatabaseLoader(engine)
    my_loader.insert_orders(orders.get_orders())

if __name__ == "__main__":
    main()
