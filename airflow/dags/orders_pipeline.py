import hashlib
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

from airflow.sdk import dag, task, get_current_context
from sqlalchemy import create_engine

from ocado_interview.filereader import FileReader
from ocado_interview.databaseloader import DatabaseLoader
from ocado_interview.orders import Order


logger = logging.getLogger(__name__)


@dag(
    dag_id="orders_pipeline",
    description="Extract, stage and load orders into PostgreSQL",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "data-engineering",
        "retries": 2,
        "retry_delay": timedelta(minutes=1),
    },
    tags=["orders", "etl"],
)
def orders_pipeline():

    @task
    def extract_orders() -> dict:
        """
        Read and validate source orders.
        Write valid and rejected records to a staging file.

        Return only metadata through XCom.
        """
        source_path = Path(
            os.getenv(
                "ORDERS_SOURCE_PATH",
                "/usr/local/airflow/include/data/orders.json",
            )
        )

        staging_dir = Path(
            os.getenv(
                "ORDERS_STAGING_DIR",
                "/usr/local/airflow/include/staging",
            )
        )

        if not source_path.is_file():
            raise FileNotFoundError(
                f"Orders source file not found: {source_path}"
            )

        context = get_current_context()
        run_id = context["run_id"]

        # Stable path across retries of the same DAG run.
        run_hash = hashlib.sha256(
            run_id.encode("utf-8")
        ).hexdigest()[:16]

        staging_dir.mkdir(parents=True, exist_ok=True)

        staging_path = staging_dir / f"orders_{run_hash}.json"
        temp_path = staging_path.with_suffix(".tmp")

        reader = FileReader(str(source_path))
        orders, rejected = reader.get_orders()

        payload = {
            "orders": [
                order.model_dump(mode="json")
                for order in orders
            ],
            "rejected": rejected,
        }

        # Atomic replacement prevents downstream tasks from
        # reading a partially written staging file.
        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False)

        temp_path.replace(staging_path)

        metadata = {
            "run_id": run_id,
            "source_path": str(source_path),
            "staging_path": str(staging_path),
            "valid_count": len(orders),
            "rejected_count": len(rejected),
        }

        logger.info(
            "Extraction completed: valid=%d, rejected=%d, staging=%s",
            metadata["valid_count"],
            metadata["rejected_count"],
            staging_path,
        )

        return metadata

    @task
    def load_orders(metadata: dict) -> dict:
        """
        Read validated orders from staging and load them into PostgreSQL.
        """
        staging_path = Path(metadata["staging_path"])

        if not staging_path.is_file():
            raise FileNotFoundError(
                f"Staging file not found: {staging_path}"
            )

        with staging_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        orders = [
            Order.model_validate(record)
            for record in payload["orders"]
        ]

        if orders:
            database_url = os.getenv(
                "ORDERS_DATABASE_URL",
                "postgresql+psycopg://ocado:ocado-dev@db:5432/orders",
            )

            engine = create_engine(
                database_url,
                pool_pre_ping=True,
            )

            try:
                loader = DatabaseLoader(engine)
                loader.insert_orders(orders)
            finally:
                engine.dispose()

        result = {
            **metadata,
            "submitted_count": len(orders),
            "load_status": "success",
        }

        logger.info(
            "Load completed: submitted=%d, rejected=%d",
            result["submitted_count"],
            result["rejected_count"],
        )

        return result

    @task
    def report_results(metadata: dict) -> None:
        """
        Report the final pipeline statistics.
        """
        logger.info("=" * 50)
        logger.info("ORDERS PIPELINE SUMMARY")
        logger.info("Run ID:          %s", metadata["run_id"])
        logger.info("Source:          %s", metadata["source_path"])
        logger.info("Staging:         %s", metadata["staging_path"])
        logger.info("Valid records:   %d", metadata["valid_count"])
        logger.info("Rejected records:%d", metadata["rejected_count"])
        logger.info("Submitted to DB: %d", metadata["submitted_count"])
        logger.info("Load status:     %s", metadata["load_status"])
        logger.info("=" * 50)

    extraction = extract_orders()
    loading = load_orders(extraction)
    report_results(loading)


orders_pipeline()