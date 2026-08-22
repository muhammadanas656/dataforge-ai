import sqlite3
import os
import json
from src.utils import logger

class FeedbackStore:
    def __init__(self, db="data/feedback.db"):
        os.makedirs("data", exist_ok=True)
        self.db = db
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT,
                    action TEXT,
                    column_name TEXT,
                    impact_pct REAL,
                    risk_level TEXT,
                    approved INTEGER,
                    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def log(self, run_id, action, column_name, impact_pct, risk_level, approved):
        with sqlite3.connect(self.db) as conn:
            conn.execute(
                "INSERT INTO feedback (run_id, action, column_name, impact_pct, risk_level, approved) VALUES (?,?,?,?,?,?)",
                (run_id, action, column_name or "", float(impact_pct or 0.0), risk_level or "low", 1 if approved else 0)
            )
            conn.commit()
        logger.info(f"Feedback logged: {action} (col={column_name}, approved={approved})")

    def get_history(self):
        with sqlite3.connect(self.db) as conn:
            return conn.execute("SELECT action, impact_pct, risk_level, approved FROM feedback").fetchall()

store = FeedbackStore()
