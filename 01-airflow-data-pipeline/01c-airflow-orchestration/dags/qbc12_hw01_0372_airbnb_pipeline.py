
from datetime import datetime
from pathlib import Path
import os
import logging

from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from airflow.exceptions import AirflowFailException
from sqlalchemy import create_engine, text
import pandas as pd

# -------------------------------------------------------------------
# Configuration – read from Airflow Variables
# -------------------------------------------------------------------
DB_HOST = Variable.get("QBC12_DB_HOST")
DB_PORT = Variable.get("QBC12_DB_PORT")
DB_NAME = Variable.get("QBC12_DB_NAME")
DB_USER = Variable.get("QBC12_DB_USER")
DB_PASSWORD = Variable.get("QBC12_DB_PASSWORD")
STUDENT_SCHEMA = Variable.get("QBC12_STUDENT_SCHEMA", default_var="student_melika_nobakhtian")
REPORTS_DIR = Variable.get("QBC12_REPORTS_DIR", default_var="/tmp/airflow_reports")
MV_NAME = "mv_airbnb_neighbourhood_summary"

# Ensure reports directory exists
Path(REPORTS_DIR).mkdir(parents=True, exist_ok=True)

DEFAULT_ARGS = {
    "owner": "student",
    "depends_on_past": False,
    "retries": 1,
    "start_date": datetime(2026, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
}

def get_engine():
    """Return a SQLAlchemy engine for the shared Postgres database."""
    return create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        pool_pre_ping=True,
    )

# -------------------------------------------------------------------
# DAG definition
# -------------------------------------------------------------------
with DAG(
    dag_id="qbc12_hw01_melika_nobakhtian_airbnb_pipeline",
    default_args=DEFAULT_ARGS,
    schedule="0 6 * * *",            # daily at 6 AM
    catchup=False,
    tags=["qbc12", "airbnb", "hw01"],
    description="Refreshes Airbnb neighbourhood materialized view and validates",
) as dag:

    @task
    def read_config() -> dict:
        """Return configuration dictionary (no secrets, just metadata)."""
        return {
            "student_schema": STUDENT_SCHEMA,
            "mv_name": MV_NAME,
            "reports_dir": REPORTS_DIR,
            "run_ts": datetime.now().isoformat(),
        }

    @task
    def refresh_summary(config: dict) -> dict:
        """
        Drop (if exists) and recreate the materialized view + indexes.
        Returns a dict with refresh status.
        """
        schema = config["student_schema"]
        mv = config["mv_name"]
        full_mv = f'"{schema}"."{mv}"'

        # SQL statements to recreate the view and indexes
        # (based on the optimized SQL from HW01‑B)
        create_mv_sql = f"""
        DROP MATERIALIZED VIEW IF EXISTS {full_mv};
        CREATE MATERIALIZED VIEW {full_mv} AS
        WITH calendar_30 AS (
            SELECT
                listing_id,
                ROUND(AVG(CASE WHEN available THEN 1.0 ELSE 0.0 END)::numeric, 4) AS availability_30_rate
            FROM core.calendar_day
            WHERE date >= CURRENT_DATE
              AND date < CURRENT_DATE + INTERVAL '30 days'
            GROUP BY listing_id
        ),
        review_counts AS (
            SELECT listing_id, COUNT(*) AS total_reviews
            FROM core.review
            GROUP BY listing_id
        )
        SELECT
            l.neighbourhood_id::text                                                               AS neighbourhood,
            COUNT(l.listing_id)                                                                    AS num_listings,
            ROUND(AVG(l.listing_price)::numeric, 2)                                                AS avg_price,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY l.listing_price)::numeric, 2)       AS median_price,
            ROUND(AVG(l.minimum_nights)::numeric, 2)                                               AS avg_minimum_nights,
            COALESCE(SUM(r.total_reviews), 0)                                                      AS total_reviews,
            ROUND(COALESCE(SUM(r.total_reviews)::numeric / NULLIF(COUNT(l.listing_id), 0), 0), 2) AS reviews_per_listing,
            ROUND(AVG(c30.availability_30_rate)::numeric, 4)                                       AS availability_30_rate
        FROM core.listing l
        LEFT JOIN calendar_30   c30 ON c30.listing_id = l.listing_id
        LEFT JOIN review_counts r   ON r.listing_id   = l.listing_id
        GROUP BY l.neighbourhood_id;
        """
        index_sql = f"""
        CREATE INDEX idx_mv_neighbourhood ON {full_mv} (neighbourhood);
        CREATE INDEX idx_mv_num_listings   ON {full_mv} (num_listings DESC);
        """

        engine = get_engine()
        with engine.begin() as conn:
            logging.info("Refreshing materialized view...")
            conn.execute(text(create_mv_sql))
            logging.info("Creating indexes...")
            conn.execute(text(index_sql))

        return {"refreshed_at": datetime.now().isoformat(), "full_mv_name": full_mv}

    @task
    def validate_summary(config: dict) -> dict:
        """
        Run quality checks on the materialized view.
        Returns a dict with check results and a boolean 'passed'.
        """
        full_mv = f'"{config["student_schema"]}"."{config["mv_name"]}"'
        engine = get_engine()

        checks = {}

        # 1. row_count > 0
        with engine.connect() as conn:
            row_count = conn.execute(text(f"SELECT COUNT(*) FROM {full_mv}")).scalar()
        checks["row_count"] = row_count
        checks["row_count_passed"] = row_count > 0

        # 2. null_neighbourhoods == 0
        with engine.connect() as conn:
            null_neigh = conn.execute(text(f"SELECT COUNT(*) FROM {full_mv} WHERE neighbourhood IS NULL")).scalar()
        checks["null_neighbourhoods"] = null_neigh
        checks["null_neighbourhoods_passed"] = null_neigh == 0

        # 3. bad_prices == 0 (price <= 0 or NULL)
        with engine.connect() as conn:
            bad_price = conn.execute(text(
                f"SELECT COUNT(*) FROM {full_mv} WHERE avg_price <= 0 OR avg_price IS NULL OR median_price <= 0 OR median_price IS NULL"
            )).scalar()
        checks["bad_prices"] = bad_price
        checks["bad_prices_passed"] = bad_price == 0

        # 4. bad_availability == 0 (rate not in [0,1] or NULL)
        with engine.connect() as conn:
            bad_avail = conn.execute(text(
                f"SELECT COUNT(*) FROM {full_mv} WHERE availability_30_rate < 0 OR availability_30_rate > 1 OR availability_30_rate IS NULL"
            )).scalar()
        checks["bad_availability"] = bad_avail
        checks["bad_availability_passed"] = bad_avail == 0

        checks["passed"] = all([
            checks["row_count_passed"],
            checks["null_neighbourhoods_passed"],
            checks["bad_prices_passed"],
            checks["bad_availability_passed"]
        ])
        return checks

    @task.branch
    def choose_report_path(validation: dict) -> str:
        """Return the task id of the next task based on validation outcome."""
        if validation["passed"]:
            return "write_success_report"
        else:
            return "write_failure_report"

    @task
    def write_success_report(config: dict, validation: dict) -> str:
        """Write a success report file and return its path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(config["reports_dir"]) / f"success_{timestamp}.txt"
        content = f"""
            Airflow DAG Success Report
            ==========================
            DAG ID: {DAG.dag_id}
            Run timestamp: {config['run_ts']}
            Materialized view: {config['student_schema']}.{config['mv_name']}

            Validation results:
            - Row count: {validation['row_count']} (>0) ✓
            - Null neighbourhoods: {validation['null_neighbourhoods']} (==0) ✓
            - Bad prices: {validation['bad_prices']} (==0) ✓
            - Bad availability: {validation['bad_availability']} (==0) ✓

            All checks passed. The materialized view is ready for Metabase.
        """
        report_file.write_text(content.strip())
        logging.info(f"Success report written to {report_file}")
        return str(report_file)

    @task
    def write_failure_report(config: dict, validation: dict):
        """Write a failure report and then raise ValueError to fail the DAG."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(config["reports_dir"]) / f"failure_{timestamp}.txt"
        failures = []
        if not validation["row_count_passed"]:
            failures.append(f"Row count = {validation['row_count']} (must be >0)")
        if not validation["null_neighbourhoods_passed"]:
            failures.append(f"Null neighbourhoods = {validation['null_neighbourhoods']} (must be 0)")
        if not validation["bad_prices_passed"]:
            failures.append(f"Bad prices = {validation['bad_prices']} (must be 0)")
        if not validation["bad_availability_passed"]:
            failures.append(f"Bad availability = {validation['bad_availability']} (must be 0)")

        content = f"""
            Airflow DAG Failure Report
            ==========================
            DAG ID: {DAG.dag_id}
            Run timestamp: {config['run_ts']}
            Materialized view: {config['student_schema']}.{config['mv_name']}

            FAILED CHECKS:
            {chr(10).join('- ' + f for f in failures)}

            Please investigate the data pipeline.
        """
        report_file.write_text(content.strip())
        logging.error(f"Failure report written to {report_file}")
        # Raise an exception to mark the DAG run as failed
        raise ValueError(f"Validation failed: {', '.join(failures)}")

    # -------------------------------------------------------------------
    # Build the DAG
    # -------------------------------------------------------------------
    conf = read_config()
    refresh = refresh_summary(conf)
    validation = validate_summary(conf)
    branch = choose_report_path(validation)

    # The branch task returns the id of the next task
    success = write_success_report(conf, validation)
    failure = write_failure_report(conf, validation)

    conf >> refresh >> validation >> branch
    branch >> success
    branch >> failure