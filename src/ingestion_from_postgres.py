import json
import os
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

from functions.s3_utils import upload_to_s3

load_dotenv(Path(__file__).resolve().parents[1] / "docker" / ".env")

# ==============================
# PostgreSQL (AdventureWorks) connection
# ==============================
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5435")
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_DATABASE = os.getenv("POSTGRES_DATABASE", "Adventureworks")

TABLE_NAME = "humanresources.employee"


def get_connection():
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DATABASE,
    )


def serialize_value(value):
    """Convert PostgreSQL-specific types to JSON serializable types."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def export_table_to_minio(table_name: str):
    """
    Export a PostgreSQL table directly to MinIO in JSON format.
    """
    if not PG_PASSWORD:
        raise SystemExit("POSTGRES_PASSWORD not defined in .env")

    conn = get_connection()
    cursor = conn.cursor()

    print(f"Reading rows from table '{table_name}'...")

    cursor.execute(f"SELECT * FROM {table_name}")
    columns = [column.name for column in cursor.description]

    documents = [
        {col: serialize_value(value) for col, value in zip(columns, row)}
        for row in cursor.fetchall()
    ]

    print(f"Total rows fetched: {len(documents)}")

    # Generate filename pattern
    key = table_name.split(".")[-1]
    filename = f"{key}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.json"

    # Convert to JSON string
    data_json = json.dumps(documents, ensure_ascii=False)

    # Upload to MinIO
    upload_to_s3(filename, data_json, source="postgres")

    print(f"Saved file to MinIO bucket as {filename}")

    cursor.close()
    conn.close()


def main():
    export_table_to_minio(TABLE_NAME)
    print("Export completed.")


if __name__ == "__main__":
    main()
