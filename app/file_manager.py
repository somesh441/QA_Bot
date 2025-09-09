import os
from typing import List

UPLOAD_DIR = "uploaded"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def list_uploaded_files() -> List[str]:
    return [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]


def delete_uploaded_file(filename: str) -> bool:
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False


def save_uploaded_file(uploaded_file) -> str:
    filename = uploaded_file.name
    safe_path = os.path.join(UPLOAD_DIR, filename)
    with open(safe_path, "wb") as f:
        f.write(uploaded_file.read())
    return filename
