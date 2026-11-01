# import argparse
import json
from typing import List
from src.ocado_interview.orders import Order, Orders


class FileReader:
    def __init__(self, source_name):
        self.filename = source_name
        self.dlq = list()
        self.orders = Orders(orders_list=[])

    def read_source(self):
        with open(self.filename, 'r') as file:
            return json.load(file)

    def get_orders(self) -> tuple[Orders, list]:
        contents = self.read_source()
        # print(f"Contents of the file: {contents}")


        for order in contents:
            try:
                self.orders.add_order(Order.model_validate(order))

            except ValueError as e:
                print(f"Validation error for order {order}: {e}")
                self.dlq.append(order)


        print(f"Valid orders: {self.orders.get_orders()}")
        print(f"Invalid orders (DLQ): {self.dlq}")
        return self.orders, self.dlq

