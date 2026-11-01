import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from ocado_interview.filereader import FileReader
from ocado_interview.orders import Order


def make_order_data(**overrides: object) -> dict[str, object]:
    return {
        "order_id": "ORD-1001",
        "customer_id": 501,
        "amount": "125.50",
        "currency": "GBP",
        "status": "completed",
        "created_at": "2026-10-30T10:15:00Z",
        **overrides,
    }


INVALID_ORDER_CASES = [
    pytest.param({"order_id": ""}, id="empty-order-id"),
    pytest.param({"order_id": "O" * 51}, id="order-id-too-long"),
    pytest.param({"customer_id": 0}, id="zero-customer-id"),
    pytest.param({"customer_id": -1}, id="negative-customer-id"),
    pytest.param({"amount": "0"}, id="zero-amount"),
    pytest.param({"amount": "-1"}, id="negative-amount"),
    pytest.param({"currency": "GB"}, id="currency-too-short"),
    pytest.param({"currency": "gbp"}, id="lowercase-currency"),
    pytest.param({"currency": "GB1"}, id="non-letter-currency"),
    pytest.param({"status": "refunded"}, id="unknown-status"),
    pytest.param({"created_at": "not-a-datetime"}, id="invalid-created-at"),
]

REQUIRED_FIELDS = [
    "order_id",
    "customer_id",
    "amount",
    "currency",
    "status",
    "created_at",
]


@pytest.mark.parametrize("overrides", INVALID_ORDER_CASES)
def test_order_model_rejects_invalid_field_constraints(overrides: dict[str, object]):
    with pytest.raises(ValidationError):
        Order.model_validate(make_order_data(**overrides))


@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_order_model_requires_all_fields(field: str):
    order_data = make_order_data()
    del order_data[field]

    with pytest.raises(ValidationError):
        Order.model_validate(order_data)


@pytest.mark.parametrize("overrides", INVALID_ORDER_CASES)
def test_json_loading_sends_invalid_orders_to_dead_letter(
    tmp_path: Path, overrides: dict[str, object]
):
    valid_order = make_order_data(order_id="ORD-VALID")
    invalid_order = make_order_data(**({"order_id": "ORD-INVALID"} | overrides))
    path = tmp_path / "orders.json"
    path.write_text(json.dumps([valid_order, invalid_order]), encoding="utf-8")

    orders, dead_letter = FileReader(str(path)).get_orders()

    assert [order.order_id for order in orders] == ["ORD-VALID"]
    assert dead_letter == [invalid_order]


@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_json_loading_sends_orders_with_missing_fields_to_dead_letter(
    tmp_path: Path, field: str
):
    invalid_order = make_order_data(order_id="ORD-INVALID")
    del invalid_order[field]
    path = tmp_path / "orders.json"
    path.write_text(json.dumps([invalid_order]), encoding="utf-8")

    orders, dead_letter = FileReader(str(path)).get_orders()

    assert orders == []
    assert dead_letter == [invalid_order]


@pytest.mark.parametrize("status", ["pending", "completed", "cancelled"])
def test_order_model_accepts_each_valid_status(status: str):
    order = Order.model_validate(make_order_data(status=status))

    assert order.status == status
