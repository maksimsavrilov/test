import json
import os
from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, delete, func, select
from sqlalchemy.engine import Engine

from ocado_interview.databaseloader import DatabaseLoader
from ocado_interview.filereader import FileReader
from ocado_interview.orders import Base, OrderModel


@pytest.fixture
def database_engine() -> Iterator[Engine]:
    database_url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://ocado:ocado-dev@127.0.0.1:5432/orders",
    )
    engine = create_engine(database_url)
    try:
        Base.metadata.create_all(engine)
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def orders_file(
    tmp_path: Path, database_engine: Engine
) -> Iterator[tuple[Path, list[str]]]:
    order_ids = [f"test-{uuid4().hex}" for _ in range(2)]
    orders = [
        {
            "order_id": order_id,
            "customer_id": customer_id,
            "amount": amount,
            "currency": "GBP",
            "status": status,
            "created_at": "2026-10-30T10:15:00Z",
        }
        for order_id, customer_id, amount, status in zip(
            order_ids,
            (501, 502),
            (125.50, 89.99),
            ("completed", "pending"),
            strict=True,
        )
    ]
    path = tmp_path / "orders.json"
    path.write_text(json.dumps(orders), encoding="utf-8")

    yield path, order_ids

    with database_engine.begin() as connection:
        connection.execute(
            delete(OrderModel).where(OrderModel.order_id.in_(order_ids))
        )


def count_orders(engine: Engine, order_ids: list[str]) -> int:
    with engine.connect() as connection:
        return connection.execute(
            select(func.count())
            .select_from(OrderModel)
            .where(OrderModel.order_id.in_(order_ids))
        ).scalar_one()


def test_first_run_loads_two_valid_orders(database_engine, orders_file):
    path, order_ids = orders_file
    orders, dead_letter = FileReader(str(path)).get_orders()

    assert len(orders) == 2
    assert dead_letter == []

    DatabaseLoader(database_engine).insert_orders(orders)

    assert count_orders(database_engine, order_ids) == 2


def test_second_run_does_not_increase_order_count(database_engine, orders_file):
    path, order_ids = orders_file
    orders, dead_letter = FileReader(str(path)).get_orders()
    assert dead_letter == []

    loader = DatabaseLoader(database_engine)
    loader.insert_orders(orders)
    count_after_first_run = count_orders(database_engine, order_ids)

    loader.insert_orders(FileReader(str(path)).get_orders()[0])

    assert count_after_first_run == 2
    assert count_orders(database_engine, order_ids) == count_after_first_run
