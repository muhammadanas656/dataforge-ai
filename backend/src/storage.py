"""
Storage backend abstraction.
- LocalBackend: backward-compatible filesystem (dev/single-instance)
- S3Backend: uploads to S3 with local temp cache (production/multi-instance)

Auto-detected via S3_BUCKET env var.
"""
import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional
from src.utils import logger

class StorageBackend:
    """Abstract interface for artifact persistence."""
    
    def write_file(self, src: str, key: str) -> str:
        raise NotImplementedError
    
    def read_file(self, key: str) -> bytes:
        raise NotImplementedError
    
    def get_local_path(self, key: str) -> Optional[str]:
        raise NotImplementedError
    
    def exists(self, key: str) -> bool:
        raise NotImplementedError
    
    def list(self, prefix: str = "") -> List[str]:
        raise NotImplementedError

from src.workspace import get_workspace, workspace_path, ensure_workspace_dir

class LocalBackend(StorageBackend):
    """Files live inside workspace paths. Backward-compatible."""

    def __init__(self, base_dir: str = "."):
        self.base = base_dir

    def write_file(self, src: str, key: str) -> str:
        dst = workspace_path(key)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        src_path = Path(src)
        if src_path.resolve() != Path(dst).resolve() and src_path.exists():
            shutil.copy2(src, dst)
        return str(dst)

    def read_file(self, key: str) -> bytes:
        p = Path(workspace_path(key))
        if not p.exists() and Path(key).exists():
            return Path(key).read_bytes()
        return p.read_bytes()

    def get_local_path(self, key: str) -> Optional[str]:
        p = workspace_path(key)
        if os.path.exists(p):
            return str(p)
        if os.path.exists(key):
            return str(key)
        return None

    def exists(self, key: str) -> bool:
        return os.path.exists(workspace_path(key)) or os.path.exists(key)

    def list(self, prefix: str = "") -> List[str]:
        base = Path(workspace_path(prefix))
        if not base.exists():
            return []
        return [str(p.relative_to(base)) for p in base.rglob("*") if p.is_file()]


class S3Backend(StorageBackend):
    """Uploads/downloads to S3, with a local temp cache for reads."""
    
    def __init__(self, bucket: str, prefix: str = "dataforge/"):
        import boto3
        self.s3 = boto3.client("s3")
        self.bucket = bucket
        self.prefix = prefix
        self.cache = Path(tempfile.gettempdir()) / "dataforge_cache"
        self.cache.mkdir(exist_ok=True)
        logger.info(f"S3 storage initialized: s3://{bucket}/{prefix}")
    
    def _s3_key(self, key: str) -> str:
        return self.prefix + key.lstrip("/")
    
    def write_file(self, src: str, key: str) -> str:
        s3_key = self._s3_key(key)
        self.s3.upload_file(src, self.bucket, s3_key)
        return f"s3://{self.bucket}/{s3_key}"
    
    def read_file(self, key: str) -> bytes:
        obj = self.s3.get_object(Bucket=self.bucket, Key=self._s3_key(key))
        return obj["Body"].read()
    
    def get_local_path(self, key: str) -> Optional[str]:
        local = self.cache / key
        if local.exists():
            return str(local)
        try:
            local.parent.mkdir(parents=True, exist_ok=True)
            self.s3.download_file(self.bucket, self._s3_key(key), str(local))
            return str(local)
        except Exception as e:
            logger.warning(f"S3 download failed for {key}: {e}")
            return None
    
    def exists(self, key: str) -> bool:
        try:
            self.s3.head_object(Bucket=self.bucket, Key=self._s3_key(key))
            return True
        except Exception:
            return False
    
    def list(self, prefix: str = "") -> List[str]:
        resp = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=self._s3_key(prefix))
        return [obj["Key"][len(self.prefix):] for obj in resp.get("Contents", [])]

def get_storage() -> StorageBackend:
    bucket = os.getenv("S3_BUCKET")
    if bucket:
        prefix = os.getenv("S3_PREFIX", "dataforge/")
        return S3Backend(bucket, prefix)
    base = os.getenv("DATAFORGE_BASE_DIR", ".")
    return LocalBackend(base)

storage = get_storage()

def save_artifact(local_path: str, key: str = None) -> str:
    if key is None:
        key = local_path
    return storage.write_file(local_path, key)

def ensure_local(key: str) -> Optional[str]:
    return storage.get_local_path(key)
