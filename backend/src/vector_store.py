"""
Pluggable Vector Store Provider (Strategy Pattern).
Default: 0-dependency local JSON store. Optional: ChromaDB / pgvector.
"""
import os
import re
import json
import hashlib
import numpy as np
from abc import ABC, abstractmethod
from datetime import datetime
from src.utils import logger
from src.workspace import workspace_path

EMBED_DIM = int(os.getenv("EMBED_DIM", "256"))


def embed_text(text, dim=EMBED_DIM):
    """Deterministic feature-hashing embedding. 0 dependencies, works offline."""
    vec = np.zeros(dim, dtype=np.float32)
    tokens = re.findall(r"[a-z0-9_]+", str(text).lower())
    for tok in tokens:
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
        idx = h % dim
        sign = 1 if (h // dim) % 2 == 0 else -1
        vec[idx] += sign
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


class VectorStore(ABC):
    """Unified interface. Swap backends without changing calling code."""
    @abstractmethod
    def add(self, doc_id, text, metadata=None): ...
    @abstractmethod
    def query(self, text, top_k=5): ...
    @abstractmethod
    def delete(self, doc_id): ...
    @abstractmethod
    def count(self): ...
    @abstractmethod
    def clear(self): ...

    def add_many(self, items):
        """Default batch = loop. Backends override for efficiency."""
        for doc_id, text, metadata in items:
            self.add(doc_id, text, metadata)


class LocalJsonVectorStore(VectorStore):
    """0-dependency, numpy-backed store. Cached matrix = <10ms retrieval."""

    def __init__(self, path=None):
        self.path = path or workspace_path("vector_store.json")
        self.docs = {}
        self._mat = None
        self._ids = []
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, encoding="utf-8") as f:
                    self.docs = json.load(f)
            except Exception:
                self.docs = {}
        self._rebuild_index()

    def _rebuild_index(self):
        self._ids = list(self.docs.keys())
        if self._ids:
            self._mat = np.array(
                [self.docs[i]["embedding"] for i in self._ids], dtype=np.float32
            )
        else:
            self._mat = None

    def _save(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.docs, f, indent=2, ensure_ascii=False)

    def add(self, doc_id, text, metadata=None):
        self.docs[doc_id] = {
            "text": text,
            "metadata": metadata or {},
            "embedding": embed_text(text).tolist(),
            "ts": datetime.now().isoformat(),
        }
        self._mat = None
        self._save()

    def add_many(self, items):
        for doc_id, text, metadata in items:
            self.docs[doc_id] = {
                "text": text,
                "metadata": metadata or {},
                "embedding": embed_text(text).tolist(),
                "ts": datetime.now().isoformat(),
            }
        self._mat = None
        self._save()

    def query(self, text, top_k=5):
        if not self.docs:
            return []
        if self._mat is None:
            self._rebuild_index()
        q = embed_text(text)
        scores = self._mat @ q
        k = min(top_k, len(scores))
        top_idx = np.argpartition(scores, -k)[-k:]
        top_idx = top_idx[np.argsort(scores[top_idx])[::-1]]
        return [
            {
                "doc_id": self._ids[i],
                "score": float(scores[i]),
                "text": self.docs[self._ids[i]]["text"],
                "metadata": self.docs[self._ids[i]]["metadata"],
            }
            for i in top_idx
        ]

    def delete(self, doc_id):
        self.docs.pop(doc_id, None)
        self._mat = None
        self._save()

    def count(self):
        return len(self.docs)

    def clear(self):
        self.docs = {}
        self._mat = None
        self._ids = []
        self._save()


class ChromaVectorStore(VectorStore):
    """ChromaDB persistent backend for enterprise scale."""

    def __init__(self, collection_name=None, persist_dir=None):
        import chromadb
        from src.workspace import get_workspace
        wid = get_workspace()
        persist_dir = persist_dir or workspace_path(f"chroma_{wid}")
        collection_name = collection_name or f"dataforge_{wid}"
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=collection_name, metadata={"hnsw:space": "cosine"}
        )

    def add(self, doc_id, text, metadata=None):
        self.collection.upsert(
            ids=[doc_id],
            documents=[text],
            embeddings=[embed_text(text).tolist()],
            metadatas=[metadata or {"empty": True}],
        )

    def add_many(self, items):
        ids = [d for d, _, _ in items]
        docs = [t for _, t, _ in items]
        embs = [embed_text(t).tolist() for _, t, _ in items]
        metas = [m or {"empty": True} for _, _, m in items]
        self.collection.upsert(ids=ids, documents=docs, embeddings=embs, metadatas=metas)

    def query(self, text, top_k=5):
        res = self.collection.query(
            query_embeddings=[embed_text(text).tolist()], n_results=top_k
        )
        out = []
        if res["ids"] and res["ids"][0]:
            for i, doc_id in enumerate(res["ids"][0]):
                out.append({
                    "doc_id": doc_id,
                    "score": 1.0 - res["distances"][0][i],
                    "text": res["documents"][0][i],
                    "metadata": res["metadatas"][0][i],
                })
        return out

    def delete(self, doc_id):
        try:
            self.collection.delete(ids=[doc_id])
        except Exception as e:
            logger.warning(f"[chroma] delete failed: {e}")

    def count(self):
        return self.collection.count()

    def clear(self):
        name = self.collection.name
        self.client.delete_collection(name)
        self.collection = self.client.get_or_create_collection(
            name=name, metadata={"hnsw:space": "cosine"}
        )


class PgVectorStore(VectorStore):
    """pgvector backend. Requires psycopg2 + pgvector extension."""

    def __init__(self, dsn=None, table=None):
        import psycopg2
        from pgvector.psycopg2 import register_vector
        from src.workspace import get_workspace
        wid = get_workspace()
        self.dsn = dsn or os.getenv("PGVECTOR_DSN")
        self.table = table or f"dataforge_vectors_{wid}"
        self.conn = psycopg2.connect(self.dsn)
        register_vector(self.conn)
        self._init_table()

    def _init_table(self):
        with self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table} (
                    doc_id TEXT PRIMARY KEY,
                    text TEXT, metadata JSONB,
                    embedding vector({EMBED_DIM})
                )
            """)
            cur.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{self.table}_emb
                ON {self.table} USING ivfflat (embedding vector_cosine_ops)
            """)
        self.conn.commit()

    def add(self, doc_id, text, metadata=None):
        emb = embed_text(text).tolist()
        meta = json.dumps(metadata or {})
        with self.conn.cursor() as cur:
            cur.execute(f"""
                INSERT INTO {self.table} (doc_id, text, metadata, embedding)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (doc_id) DO UPDATE
                SET text=EXCLUDED.text, metadata=EXCLUDED.metadata, embedding=EXCLUDED.embedding
            """, (doc_id, text, meta, emb))
        self.conn.commit()

    def query(self, text, top_k=5):
        emb = embed_text(text).tolist()
        with self.conn.cursor() as cur:
            cur.execute(f"""
                SELECT doc_id, text, metadata, 1 - (embedding <=> %s::vector) AS score
                FROM {self.table}
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (emb, emb, top_k))
            rows = cur.fetchall()
        return [{"doc_id": r[0], "text": r[1], "metadata": r[2], "score": float(r[3])} for r in rows]

    def delete(self, doc_id):
        with self.conn.cursor() as cur:
            cur.execute(f"DELETE FROM {self.table} WHERE doc_id=%s", (doc_id,))
        self.conn.commit()

    def count(self):
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {self.table}")
            return cur.fetchone()[0]

    def clear(self):
        with self.conn.cursor() as cur:
            cur.execute(f"TRUNCATE TABLE {self.table}")
        self.conn.commit()


def get_vector_store() -> VectorStore:
    backend = os.getenv("VECTOR_DB", "local").lower()
    if backend == "chroma":
        logger.info("[vector_store] Using ChromaDB backend")
        return ChromaVectorStore()
    if backend in ("pgvector", "postgres"):
        logger.info("[vector_store] Using pgvector backend")
        return PgVectorStore()
    logger.info("[vector_store] Using local JSON backend")
    return LocalJsonVectorStore()


vector_store = get_vector_store()
