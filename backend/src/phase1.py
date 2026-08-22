import os
import json
import uuid
import sys
from datetime import datetime
from src.utils import logger
from src import security, sources, profiler, plugins, ingest_big, relational, storage

def run_phase1(path: str):
    meta = security.check_upload(path)
    dataset_id = uuid.uuid4().hex[:8]
    os.makedirs("data/canonical", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # ── BIG PATH: Out-of-core streaming via DuckDB ────────
    if ingest_big.is_big(path) and ingest_big._reader(path):
        pq = f"data/canonical/{dataset_id}.parquet"
        if ingest_big.ingest_to_parquet(path, pq):
            sample = sources.canonicalize(ingest_big.sample_from_parquet(pq))
            prof = ingest_big.profile_big(pq)
            for c in prof.get("columns", []):
                if c["name"] in sample.columns:
                    c["sample_values"] = [str(v) for v in sample[c["name"]].dropna().unique()[:5]]
            sample_csv = f"data/canonical/{dataset_id}.csv"
            sample.to_csv(sample_csv, index=False)
            prof.update({
                "dataset_id": dataset_id,
                "source": "duckdb_big",
                "big": True,
                "encoding": "utf-8",
                "filename": os.path.basename(path),
                "created_at": datetime.now().isoformat(),
                "schema_fingerprint": security.schema_fingerprint(sample),
                "near_duplicate_estimate": 0,
                "pii": {},
                "snapshot": {"parquet": pq, "csv": sample_csv}
            })
            report_path = f"reports/profile_{dataset_id}.json"
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(prof, f, indent=2, ensure_ascii=False, default=str)
            storage.save_artifact(report_path)
            logger.info(f"Phase 1 (BIG) complete. dataset_id={dataset_id} rows={prof['total_rows']}")
            return prof

    # ── STANDARD PATH: pandas + plugins ──────────────────
    encoding = security.detect_encoding(path)
    logger.info(f"Encoding detected: {encoding} for {path}")
    load_encoding = None if encoding == "binary" else encoding
    result = plugins.load_with_plugins(path, encoding=load_encoding)

    df = sources.canonicalize(result.df)
    pq, csv = sources.save_snapshot(df, dataset_id)
    profile = profiler.profile_dataframe(df)
    profile.update({
        "dataset_id": dataset_id,
        "source": result.source_name,
        "encoding": encoding,
        "filename": os.path.basename(path),
        "created_at": datetime.now().isoformat(),
        "schema_fingerprint": security.schema_fingerprint(df),
        "snapshot": {"parquet": pq, "csv": csv}
    })

    report_path = f"reports/profile_{dataset_id}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False, default=str)
    storage.save_artifact(report_path)

    logger.info(f"Phase 1 complete. dataset_id={dataset_id}")
    return profile

def run_phase1_multi(paths: list):
    """Load multiple relational files, infer FKs, flag orphans, and flatten into unified schema."""
    tables = {}
    for p in paths:
        r = sources.detect_and_load(p)
        name = os.path.splitext(os.path.basename(p))[0]
        tables[name] = sources.canonicalize(r.df)

    fks = relational.detect_foreign_keys(tables)
    summary = relational.summarize(tables, fks)

    # Primary table = table that is most often referenced or has child FKs
    child_count = {t: 0 for t in tables}
    for fk in fks:
        child_count[fk["child"]] += 1
    primary = max(child_count, key=child_count.get) if child_count else list(tables.keys())[0]

    flat = relational.flatten(tables, fks, primary)
    flat = sources.canonicalize(flat)

    dataset_id = uuid.uuid4().hex[:8]
    os.makedirs("data/canonical", exist_ok=True)
    pq = f"data/canonical/{dataset_id}.parquet"
    csv = f"data/canonical/{dataset_id}.csv"
    flat.to_parquet(pq, index=False)
    flat.to_csv(csv, index=False)

    prof = profiler.profile_dataframe(flat)
    prof.update({
        "dataset_id": dataset_id,
        "multi_table": True,
        "primary": primary,
        "relations": summary,
        "filename": f"relational_{len(tables)}_tables",
        "created_at": datetime.now().isoformat(),
        "encoding": "utf-8",
        "schema_fingerprint": security.schema_fingerprint(flat),
        "snapshot": {"parquet": pq, "csv": csv}
    })

    os.makedirs("reports", exist_ok=True)
    report_path = f"reports/profile_{dataset_id}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(prof, f, indent=2, ensure_ascii=False, default=str)
    storage.save_artifact(report_path)

    logger.info(f"Phase 1 (MULTI) complete: {len(tables)} tables -> primary={primary}")
    return prof

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/raw_ecommerce.csv"
    run_phase1(path)
