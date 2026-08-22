import os
import pyarrow.parquet as pq
from src.utils import logger

LARGE_THRESHOLD = 500 * 1024 * 1024  # 500MB

def parquet_size(path):
    try:
        return os.path.getsize(path)
    except Exception:
        return 0

def count_violations_chunked(parquet_path, expr, max_rows=None):
    """Stream a Parquet snapshot in 100k-row batches; never load it all into RAM."""
    total = 0
    violations = 0
    try:
        pf = pq.ParquetFile(parquet_path)
        for batch in pf.iter_batches(batch_size=100_000):
            dfc = batch.to_pandas()
            total += len(dfc)
            try:
                violations += len(dfc.query(f"not ({expr})"))
            except Exception:
                return None
            if max_rows and total >= max_rows:
                break
        return violations, total
    except Exception as e:
        logger.error(f"chunked count failed: {e}")
        return None
