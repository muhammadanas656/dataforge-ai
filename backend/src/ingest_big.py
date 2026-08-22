import os
import duckdb
from src.utils import logger

BIG = 500 * 1024 * 1024  # 500MB threshold

def is_big(path: str) -> bool:
    try:
        return os.path.getsize(path) > BIG
    except Exception:
        return False

def _reader(path: str):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".csv", ".tsv"):
        return f"read_csv_auto('{path}', header=true, sample_size=-1)"
    if ext == ".parquet":
        return f"read_parquet('{path}')"
    if ext == ".json":
        return f"read_json_auto('{path}')"
    return None  # Excel isn't streamable -> fall back to standard pandas path

def ingest_to_parquet(path: str, out_parquet: str):
    """Stream CSV/Parquet/JSON -> canonical Parquet WITHOUT loading into RAM."""
    reader = _reader(path)
    if reader is None:
        return None
    os.makedirs(os.path.dirname(out_parquet), exist_ok=True)
    con = duckdb.connect()
    try:
        con.execute(f"COPY (SELECT * FROM {reader}) TO '{out_parquet}' (FORMAT PARQUET)")
        return out_parquet
    except Exception as e:
        logger.error(f"duckdb ingest failed: {e}")
        return None
    finally:
        con.close()

def _kind(dtype: str) -> str:
    d = dtype.upper()
    if any(x in d for x in ("INT", "FLOAT", "DOUBLE", "DECIMAL", "NUMERIC", "REAL", "BIGINT", "SMALLINT", "TINYINT", "HUGEINT")):
        return "numeric"
    return "text"

def profile_big(parquet: str):
    """True full-data statistics via DuckDB SQL aggregates (no RAM overhead)."""
    con = duckdb.connect()
    try:
        rows = con.execute(f"SELECT COUNT(*) FROM '{parquet}'").fetchone()[0]
        cols = con.execute(f"DESCRIBE SELECT * FROM '{parquet}'").fetchall()
        columns = []
        for name, dtype, _, _, _, _ in cols:
            nulls = con.execute(f'SELECT COUNT(*) FROM "{parquet}" WHERE "{name}" IS NULL').fetchone()[0]
            uniq = con.execute(f'SELECT APPROX_COUNT_DISTINCT("{name}") FROM "{parquet}"').fetchone()[0] or 0
            columns.append({
                "name": name,
                "dtype": dtype,
                "kind": _kind(dtype),
                "nulls": int(nulls),
                "null_pct": round(nulls / rows * 100, 2) if rows else 0,
                "unique": int(uniq),
                "unique_pct": round(uniq / rows * 100, 2) if rows else 0
            })
        dupes = con.execute(f"SELECT COALESCE(SUM(c-1),0) FROM (SELECT COUNT(*) AS c FROM '{parquet}' GROUP BY ALL)").fetchone()[0]
        return {
            "total_rows": int(rows),
            "total_columns": len(columns),
            "columns": columns,
            "duplicate_rows": int(dupes),
            "duplicate_pct": round(dupes / rows * 100, 2) if rows else 0
        }
    finally:
        con.close()

def sample_from_parquet(parquet: str, n: int = 50000):
    con = duckdb.connect()
    try:
        return con.execute(f"SELECT * FROM '{parquet}' USING SAMPLE {n} ROWS").fetchdf()
    finally:
        con.close()
