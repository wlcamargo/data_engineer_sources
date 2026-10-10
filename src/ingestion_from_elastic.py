from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from datetime import datetime
from pathlib import Path
import json
import os
from dotenv import load_dotenv

from functions.s3_utils import upload_to_s3

load_dotenv(Path(__file__).resolve().parents[1] / "docker" / ".env")

# ==============================
# Elasticsearch connection
# ==============================
ES_HOST = os.getenv("ELASTIC_URL", "http://localhost:9200")
ES_USER = os.getenv("ELASTIC_USERNAME", "elastic")
ES_PASS = os.getenv("ELASTIC_PASSWORD")

INDEX_NAME = "sample-products"

es = Elasticsearch(
    ES_HOST,
    http_auth=(ES_USER, ES_PASS)
)


def export_index_to_minio(index_name: str):
    """
    Export Elasticsearch index directly to MinIO in JSON format.
    """

    print(f"Reading documents from index '{index_name}'...")

    # 1. Read documents using scan (better for large datasets)
    documents = []

    for doc in scan(es, index=index_name, query={"query": {"match_all": {}}}):
        source = doc["_source"]
        source["_id"] = doc["_id"]  # optional: keep ES id
        documents.append(source)

    print(f"Total documents fetched: {len(documents)}")

    # 2. Generate filename pattern
    key = index_name.replace("-", "_")
    filename = f"{key}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.json"

    # 3. Convert to JSON string
    data_json = json.dumps(documents, ensure_ascii=False)

    # 4. Upload to MinIO
    upload_to_s3(filename, data_json, source="elasticsearch")

    print(f"Saved file to MinIO bucket as {filename}")


def main():
    if not es.indices.exists(index=INDEX_NAME):
        raise ValueError(f"Index '{INDEX_NAME}' does not exist.")

    export_index_to_minio(INDEX_NAME)

    print("Export completed.")


if __name__ == "__main__":
    main()