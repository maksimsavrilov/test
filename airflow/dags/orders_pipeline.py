from datetime import datetime

from airflow.sdk import dag, task


@dag(
    dag_id="orders_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["orders"],
)
def orders_pipeline():

    @task
    def extract_orders():
        print("Extracting orders")
        return "orders.json"

    @task
    def validate_orders(file_path: str):
        print(f"Validating orders from {file_path}")
        return file_path

    @task
    def load_orders(file_path: str):
        print(f"Loading orders from {file_path}")

    file_path = extract_orders()
    validated_file = validate_orders(file_path)
    load_orders(validated_file)


orders_pipeline()