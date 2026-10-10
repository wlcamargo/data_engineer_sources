import boto3
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / "docker" / ".env")

S3_SERVER_URL = os.getenv("MINIO_ENDPOINT", "http://127.0.0.1:9000")
AWS_ACCESS_KEY_ID = os.getenv("MINIO_ROOT_USER", "minioadmin")
AWS_SECRET_ACCESS_KEY = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
BUCKET_NAME = "raw"


s3_client = boto3.client(
    's3',
    endpoint_url=S3_SERVER_URL,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def upload_to_s3(filename, data, source=None, content_type="application/octet-stream"):
    """
    Upload data to the raw bucket, namespaced by source when provided
    (e.g. source="mongodb" -> raw/mongodb/<filename>).
    """
    key = f"{source}/{filename}" if source else filename

    s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=data,
            ContentType=content_type
        )

