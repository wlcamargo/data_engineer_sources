import sys
from pathlib import Path

# Resolve project root (lab_data_engineer/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from functions.s3_utils import upload_to_s3


def upload_folder(folder_path: Path) -> int:
    if not folder_path.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    files = list(folder_path.glob("*.csv")) + list(folder_path.glob("*.xlsx"))

    if not files:
        raise FileNotFoundError(f"No CSV or XLSX files found in {folder_path}")

    uploaded = 0

    for file_path in files:
        if file_path.suffix.lower() == ".csv":
            content_type = "text/csv"
        else:
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        upload_to_s3(
            file_path.name,
            file_path.read_bytes(),
            source="local_file",
            content_type=content_type
        )

        print(f"Uploaded {file_path.name} to MinIO")
        uploaded += 1

    return uploaded


if __name__ == "__main__":
    folder_path = PROJECT_ROOT / "local_data"

    print("Using folder:", folder_path)

    total = upload_folder(folder_path)
    print(f"Uploaded {total} files to MinIO")