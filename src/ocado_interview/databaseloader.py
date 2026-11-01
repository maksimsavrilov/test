
from src.ocado_interview.orders import Order, OrderModel

class DatabaseLoader:
    def __init__(self, engine):
        self.engine = engine

    def insert_orders(self, orders: list[Order]):
        with self.engine.connect() as connection:
            for order in orders:
                print(f"Inserting order: {order}")
                print(repr(order))
                try:
                    connection.execute(
                        OrderModel.__table__.insert(),
                        {
                            "order_id": order.order_id,
                            "customer_id": order.customer_id,
                            "amount": order.amount,
                            "currency": order.currency,
                            "status": order.status,
                            "created_at": order.created_at
                        }
                    )
                    connection.commit()
                except Exception as e:
                    print(f"Error inserting order {order.order_id}: {e}")