import json
import os
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pyodbc
from dotenv import load_dotenv

from functions.s3_utils import upload_to_s3

load_dotenv(Path(__file__).resolve().parents[1] / "docker" / ".env")

# ==============================
# SQL Server connection
# ==============================
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "1435")
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("MSSQL_SA_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "master")

TABLE_NAME = "dbo.sample_orders"


def get_connection():
    conn_str = (
        f"Driver={{{DB_DRIVER}}};"
        f"Server={DB_HOST},{DB_PORT};"
        f"Database={DB_NAME};"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD};"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str, timeout=10)


def serialize_value(value):
    """Convert SQL Server-specific types to JSON serializable types."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def export_table_to_minio(table_name: str):
    """
    Export a SQL Server table directly to MinIO in JSON format.
    """
    if not DB_PASSWORD:
        raise SystemExit("MSSQL_SA_PASSWORD not defined in .env")

    conn = get_connection()
    cursor = conn.cursor()

    print(f"Reading rows from table '{table_name}'...")

    cursor.execute(f"SELECT * FROM {table_name}")
    columns = [column[0] for column in cursor.description]

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
    upload_to_s3(filename, data_json, source="sqlserver")

    print(f"Saved file to MinIO bucket as {filename}")

    cursor.close()
    conn.close()


def main():
    export_table_to_minio(TABLE_NAME)
    print("Export completed.")


if __name__ == "__main__":
    main()
