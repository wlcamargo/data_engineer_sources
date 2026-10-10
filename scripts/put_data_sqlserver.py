import os
import random
from datetime import datetime, timedelta
from pathlib import Path

import pyodbc
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / "docker" / ".env")

# Connection configuration
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "1435")
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("MSSQL_SA_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "master")

if not DB_PASSWORD:
    raise SystemExit("MSSQL_SA_PASSWORD not defined in .env")

TABLE_NAME = "dbo.sample_orders"
NUM_ROWS = 100

PRODUCTS = ["Keyboard", "Mouse", "Monitor", "Headset", "Webcam", "Docking Station", "Laptop Stand"]
CUSTOMERS = ["Alice Johnson", "Bruno Costa", "Carla Souza", "Diego Lima", "Elena Fontes", "Fábio Reis"]
STATUSES = ["pending", "shipped", "delivered", "cancelled"]


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


def generate_order(order_id: int):
    order_date = datetime.now() - timedelta(days=random.randint(0, 180))
    return (
        order_id,
        random.choice(CUSTOMERS),
        random.choice(PRODUCTS),
        random.randint(1, 10),
        round(random.uniform(19.9, 899.9), 2),
        random.choice(STATUSES),
        order_date,
    )


def main():
    conn = get_connection()
    cursor = conn.cursor()
    print("Connected to SQL Server successfully.")

    # Reset table for a clean, idempotent reload (dummy data only)
    cursor.execute(
        f"""
        IF OBJECT_ID('{TABLE_NAME}', 'U') IS NOT NULL
            DROP TABLE {TABLE_NAME}
        """
    )
    cursor.execute(
        f"""
        CREATE TABLE {TABLE_NAME} (
            order_id INT PRIMARY KEY,
            customer_name VARCHAR(100),
            product VARCHAR(100),
            quantity INT,
            unit_price DECIMAL(10,2),
            status VARCHAR(20),
            order_date DATETIME
        )
        """
    )
    conn.commit()
    print(f"Table '{TABLE_NAME}' created.")

    rows = [generate_order(i + 1) for i in range(NUM_ROWS)]
    cursor.executemany(
        f"INSERT INTO {TABLE_NAME} (order_id, customer_name, product, quantity, unit_price, status, order_date) "
        f"VALUES (?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    print(f"Inserted {len(rows)} dummy rows into '{TABLE_NAME}'.")

    cursor.close()
    conn.close()
    print("Connection closed.")


if __name__ == "__main__":
    main()
