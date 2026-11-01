from ocado_interview.orders import Order, OrderModel
from sqlalchemy.dialects.postgresql import insert

class DatabaseLoader:
    def __init__(self, engine):
        self.engine = engine

    def insert_orders(self, orders: list[Order]):
        stmt = insert(OrderModel).values([order.model_dump() for order in orders])

        stmt = stmt.on_conflict_do_nothing(
            index_elements=["order_id"]
        )
        with self.engine.begin() as connection:
            result = connection.execute(stmt)
            return result.rowcount
            