# import argparse
import json
from ocado_interview.orders import Order


class FileReader:
    def __init__(self, source_name):
        self.filename = source_name

    def read_source(self):
        with open(self.filename, 'r') as file:
            return json.load(file)

    def get_orders(self) -> tuple[list[Order], list]:

        try:
           contents = self.read_source()
        except json.JSONDecodeError as e:
            print(f"Error reading source file: {e}")
            return [], []
        # print(f"Contents of the file: {contents}")


        self.dlq = list()
        self.orders = list()
        for order in contents:
            try:
                self.orders.append(Order.model_validate(order))

            except ValueError as e:
                print(f"Validation error for order {order}: {e}")
                self.dlq.append(order)


        print(f"Valid orders: {len(self.orders)}")
        print(f"Invalid orders: {len(self.dlq)}")
        return self.orders, self.dlq

