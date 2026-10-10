from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus
import json
import os
from dotenv import load_dotenv

from functions.s3_utils import upload_to_s3

load_dotenv(Path(__file__).resolve().parents[1] / "docker" / ".env")


def connect_to_mongodb(username: str, password: str, host: str = "localhost", port: int = 27017):
    """
    Establish a connection to MongoDB using authentication.
    """
    uri = f"mongodb://{quote_plus(username)}:{quote_plus(password)}@{host}:{port}/?authSource=admin"
    client = MongoClient(uri)

    client.admin.command("ping")
    print("Connected to MongoDB successfully.")

    return client


def serialize_document(document: dict) -> dict:
    """
    Convert MongoDB-specific types to JSON serializable types.
    """
    if "_id" in document:
        document["_id"] = str(document["_id"])

    if "created_at" in document and isinstance(document["created_at"], datetime):
        document["created_at"] = document["created_at"].isoformat()

    return document


def export_collection_to_minio(collection):
    """
    Export MongoDB collection directly to MinIO using S3-compatible upload.
    """

    # 1. Read documents
    documents = list(collection.find())

    # 2. Serialize
    serialized_documents = [serialize_document(doc) for doc in documents]

    # 3. Generate filename pattern
    key = "complaints"
    filename = f"{key}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.json"

    # 4. Convert to JSON string
    data_json = json.dumps(serialized_documents, ensure_ascii=False)

    # 5. Upload to MinIO
    upload_to_s3(filename, data_json, source="mongodb")

    print(f"Saved file to MinIO bucket as {filename}")


def main():
    username = os.getenv("MONGO_INITDB_ROOT_USERNAME", "chapolin")
    password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
    if not password:
        raise SystemExit("MONGO_INITDB_ROOT_PASSWORD not defined in .env")
    database_name = "complaints_db"
    collection_name = "complaints"

    client = connect_to_mongodb(username, password)

    db = client[database_name]
    collection = db[collection_name]

    export_collection_to_minio(collection)

    client.close()
    print("Connection closed.")


if __name__ == "__main__":
    main()