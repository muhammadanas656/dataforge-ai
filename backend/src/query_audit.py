"""Query execution audit with SQLite persistence and automatic retention."""
import time
import sqlite3
import json
import os
from datetime import datetime
from src.token_tracker import tracker
from src.utils import logger

DB_PATH = "data/kb/query_audit.db"
MAX_RECORDS_PER_DATASET = 2000  # Retention policy

class QueryAuditLogger:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_id TEXT, dataset_id TEXT, query_type TEXT,
                query TEXT, schema_json TEXT, runtime_ms REAL,
                rows_scanned INTEGER, rows_returned INTEGER,
                explanation TEXT, timestamp TEXT
            )
        """)
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_dataset ON queries(dataset_id)")
        self.conn.commit()

    def explain_query(self, query, query_type="sql"):
        if not query:
            return "Execution completed."
        if query_type == "sql":
            u = query.upper()
            if "GROUP BY" in u: return "Groups data by category and aggregates numerical totals"
            if "ORDER BY" in u and "DESC" in u: return "Sorts the results from highest to lowest"
            if "ORDER BY" in u: return "Sorts the results in ascending order"
            if "JOIN" in u: return "Combines data across multiple tables"
            if "COUNT" in u: return "Counts matching records matching criteria"
            if "AVG" in u or "SUM" in u: return "Computes mathematical aggregate measures"
            return "Filters and retrieves data from the dataset"
        else:  # pandas
            if ".query(" in query: return "Filters dataset rows based on logical conditions"
            if ".groupby(" in query: return "Groups records by dimensions and computes aggregates"
            if ".sort_values(" in query: return "Sorts rows based on specified column values"
            if ".drop_duplicates(" in query: return "Removes redundant duplicate business records"
            if ".fillna(" in query: return "Imputes missing values with statistical measures"
            return "Transforms the dataset schema or rows via Pandas"

    def log_query(self, query, schema, metrics, dataset_id, query_type="sql"):
        start = metrics.get("start_time", time.time())
        end = metrics.get("end_time", time.time())
        runtime_ms = metrics.get("runtime_ms", (end - start) * 1000)
        query_id = f"q_{int(time.time() * 1000)}"
        explanation = self.explain_query(query, query_type)
        
        self.conn.execute("""
            INSERT INTO queries (query_id, dataset_id, query_type, query, schema_json, 
                                 runtime_ms, rows_scanned, rows_returned, explanation, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            query_id, dataset_id, query_type, query, json.dumps(schema or {}),
            round(float(runtime_ms), 2), int(metrics.get("rows_scanned", 0)), int(metrics.get("rows_returned", 0)),
            explanation, datetime.now().isoformat()
        ))
        
        # Enforce retention policy per dataset
        if dataset_id:
            self.conn.execute("""
                DELETE FROM queries WHERE dataset_id = ? AND id NOT IN (
                    SELECT id FROM queries WHERE dataset_id = ? ORDER BY id DESC LIMIT ?
                )
            """, (dataset_id, dataset_id, MAX_RECORDS_PER_DATASET))
        
        self.conn.commit()
        
        try:
            tracker.record(
                run_id=dataset_id,
                stage="query_execution",
                agent=query_type,
                model="sql-engine",
                pt=int(metrics.get("tokens", 0)),
                ct=0,
                cached=0,
                saved=0
            )
        except Exception as e:
            logger.warning(f"[query_audit] Token tracking failed: {e}")
        
        logger.info(f"[query_audit] {query_type} query: {runtime_ms:.2f}ms, {metrics.get('rows_returned', 0)} rows")
        return query_id

    def get_recent(self, dataset_id=None, limit=100):
        if dataset_id:
            cur = self.conn.execute("SELECT * FROM queries WHERE dataset_id=? ORDER BY id DESC LIMIT ?", (dataset_id, limit))
        else:
            cur = self.conn.execute("SELECT * FROM queries ORDER BY id DESC LIMIT ?", (limit,))
        
        results = []
        for row in cur.fetchall():
            d = dict(row)
            try:
                d["schema"] = json.loads(d.get("schema_json") or "{}")
            except Exception:
                d["schema"] = {}
            results.append(d)
        return results

    def purge_old(self, dataset_id, keep=1000):
        self.conn.execute("""
            DELETE FROM queries WHERE dataset_id = ? AND id NOT IN (
                SELECT id FROM queries WHERE dataset_id = ? ORDER BY id DESC LIMIT ?
            )
        """, (dataset_id, dataset_id, keep))
        self.conn.commit()

audit_logger = QueryAuditLogger()
