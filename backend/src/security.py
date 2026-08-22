import os
import re
import hashlib
import chardet

ALLOWED_EXT = {".csv", ".tsv", ".json", ".xlsx", ".xls", ".parquet"}
MAX_SIZE = 200 * 1024 * 1024
ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")

def validate_dataset_id(dataset_id: str) -> str:
    """Validate dataset ID format to prevent path traversal."""
    if not dataset_id or not isinstance(dataset_id, str):
        raise ValueError("Dataset ID must be a non-empty string.")
    cleaned = dataset_id.strip()
    if not ID_PATTERN.match(cleaned):
        raise ValueError(f"Invalid dataset ID format: '{dataset_id}'. Must be alphanumeric with '-' or '_'.")
    return cleaned

def sanitize_filename(name: str) -> str:
    """Sanitize filename to prevent directory traversal and special character issues."""
    base = os.path.basename(name)
    cleaned = re.sub(r"[^a-zA-Z0-9._-]", "_", base).strip("._")
    return cleaned or "dataset"

def check_upload(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    ext = os.path.splitext(path)[1].lower()
    if ext not in ALLOWED_EXT:
        raise ValueError(f"Unsupported type {ext}")
    size = os.path.getsize(path)
    if size > MAX_SIZE:
        raise ValueError("File too large")
    return {"ext": ext, "size": size}

def detect_encoding(path):
    # Binary formats don't need chardet
    ext = os.path.splitext(path)[1].lower()
    if ext in {".parquet", ".xlsx", ".xls"}:
        return "binary"
    with open(path, "rb") as f:
        raw = f.read(100000)
    detected = chardet.detect(raw).get("encoding")
    return detected or "utf-8"

def schema_fingerprint(df):
    sig = "|".join(f"{c}:{df[c].dtype}" for c in df.columns)
    return hashlib.md5(sig.encode()).hexdigest()
