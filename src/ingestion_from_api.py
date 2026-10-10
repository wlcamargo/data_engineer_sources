import json
import sys
import time
from pathlib import Path

import requests

from functions.s3_utils import upload_to_s3

URL = "https://e5e2f3a3-454c-43de-b139-659366de071e-00-t572qw8e44wh.janeway.replit.dev/dadospessoais"
filename = "personal_data.json"
MAX_RETRIES = 3
TIMEOUT_SECONDS = 10

response = None
for attempt in range(1, MAX_RETRIES + 1):
    try:
        response = requests.get(URL, timeout=TIMEOUT_SECONDS)
        if response.status_code != 503:
            break
        print(f"Attempt {attempt}/{MAX_RETRIES} returned 503. Retrying...")
        time.sleep(2)
    except requests.RequestException as exc:
        print(f"Attempt {attempt}/{MAX_RETRIES} failed: {exc}")
        time.sleep(2)

if response is None:
    raise SystemExit("Failed to reach the API after retries.")

if response.status_code == 200:
    data = response.json()
    payload = json.dumps(data)

    upload_to_s3(filename, payload, source="api")

    print(f"Saved message to MinIO bucket as {filename}")
    print("\nData preview:")
    print(payload)
else:
    message = response.text.strip() or "No response body"
    print(f"Error: {response.status_code}. Details: {message}")