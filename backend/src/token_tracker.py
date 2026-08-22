import sqlite3
import os
from src.utils import logger

PRICES = {  # USD per 1M tokens (input, output)
    "llama-3.3-70b-versatile": (0.59, 0.79),
    "llama-3.1-8b-instant": (0.05, 0.08),
    "openai/gpt-oss-20b": (0.10, 0.50),
    "default": (0.30, 0.60),
}

class TokenTracker:
    def __init__(self, db="data/token_log.db"):
        os.makedirs("data", exist_ok=True)
        self.db = db
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.db, timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn

    def _init_db(self):
        conn = self._get_conn()
        conn.execute("""CREATE TABLE IF NOT EXISTS token_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            stage TEXT,
            agent TEXT,
            model TEXT,
            prompt_tokens INT,
            completion_tokens INT,
            total INT,
            cached INT,
            tokens_saved INT,
            ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        conn.commit()
        conn.close()

    def record(self, run_id, stage, agent, model, pt, ct, cached=0, saved=0):
        try:
            conn = self._get_conn()
            conn.execute(
                "INSERT INTO token_log(run_id,stage,agent,model,prompt_tokens,completion_tokens,total,cached,tokens_saved) VALUES(?,?,?,?,?,?,?,?,?)",
                (run_id, stage, agent, model, pt, ct, pt + ct, cached, saved)
            )
            conn.commit()
            conn.close()
            logger.info(f"TokenTracker recorded {pt+ct} tokens (prompt={pt}, comp={ct}, saved={saved}) for [{stage}:{agent}]")
            self.alert_if_expensive(run_id)
        except Exception as e:
            logger.error(f"TokenTracker write failed: {e}")

    def record_cache_hit(self, run_id, stage, agent, model, saved=150):
        self.record(run_id, stage, agent, model, 0, 0, cached=1, saved=saved)

    def alert_if_expensive(self, run_id, threshold=50000):
        """Log a budget warning if a dataset run exceeds configurable token threshold."""
        if not run_id:
            return
        try:
            conn = self._get_conn()
            res = conn.execute("SELECT SUM(total) FROM token_log WHERE run_id=?", (run_id,)).fetchone()
            conn.close()
            total = res[0] if res and res[0] is not None else 0
            if total > threshold:
                logger.warning(f"⚠️ [BUDGET ALERT] Run '{run_id}' exceeded token budget: {total:,} > {threshold:,}")
        except Exception as e:
            logger.warning(f"Token budget alert check failed: {e}")

    def summary(self, run_id=None, stage=None, scope="all"):
        try:
            conn = self._get_conn()
            conditions = []
            params = []
            
            if scope == "research" or stage == "RESEARCH":
                conditions.append("stage = 'RESEARCH'")
            elif scope == "dataset" and run_id:
                conditions.append("run_id = ? AND stage != 'RESEARCH'")
                params.append(run_id)
            elif run_id:
                conditions.append("run_id = ?")
                params.append(run_id)
                
            if stage and stage != "RESEARCH":
                conditions.append("stage = ?")
                params.append(stage)
                
            w = (" WHERE " + " AND ".join(conditions)) if conditions else ""
            p = tuple(params)
            
            rows = conn.execute(
                f"SELECT stage, SUM(total), SUM(cached), SUM(tokens_saved), COUNT(*), SUM(prompt_tokens), SUM(completion_tokens) FROM token_log{w} GROUP BY stage",
                p
            ).fetchall()
            
            tot = conn.execute(
                f"SELECT SUM(total), SUM(tokens_saved), SUM(cached), COUNT(*), SUM(prompt_tokens), SUM(completion_tokens) FROM token_log{w}",
                p
            ).fetchone()
            
            cost = self._cost(conn, conditions, params)
            conn.close()

            total_tokens = tot[0] or 0
            total_saved = tot[1] or 0
            total_cache_hits = tot[2] or 0
            total_calls = tot[3] or 0
            total_prompt_tokens = tot[4] or 0
            total_completion_tokens = tot[5] or 0
            cache_hit_rate = round((total_cache_hits / total_calls * 100), 1) if total_calls > 0 else 0.0
            
            return {
                "scope": scope,
                "by_stage": [
                    {
                        "stage": r[0],
                        "total": r[1] or 0,
                        "cached_hits": r[2] or 0,
                        "tokens_saved": r[3] or 0,
                        "calls": r[4],
                        "prompt_tokens": r[5] or 0,
                        "completion_tokens": r[6] or 0
                    }
                    for r in rows
                ],
                "total_tokens": total_tokens,
                "total_input_tokens": total_prompt_tokens,
                "total_output_tokens": total_completion_tokens,
                "total_saved": total_saved,
                "cache_hit_rate_pct": cache_hit_rate,
                "estimated_cost_usd": cost
            }
        except Exception as e:
            logger.error(f"TokenTracker summary failed: {e}")
            return {
                "scope": scope,
                "by_stage": [],
                "total_tokens": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_saved": 0,
                "estimated_cost_usd": 0.0
            }

    def _cost(self, conn, conditions=None, params=None):
        w = (" WHERE " + " AND ".join(conditions)) if conditions else ""
        p = tuple(params) if params else ()
        cost = 0.0
        for m, pt, ct in conn.execute(
            f"SELECT model, SUM(prompt_tokens), SUM(completion_tokens) FROM token_log{w} GROUP BY model",
            p
        ).fetchall():
            pi, po = PRICES.get(m, PRICES["default"])
            pt_val = pt or 0
            ct_val = ct or 0
            cost += (pt_val / 1e6 * pi) + (ct_val / 1e6 * po)
        return round(cost, 6)

tracker = TokenTracker()
