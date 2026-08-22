"""
Background job queue with worker pool, cancellation, and progress reporting.
"""
import threading
import time
import uuid
from queue import Queue
import traceback
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Callable, Dict, Optional
from src.utils import logger

class Status(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"
    CANCELLED = "cancelled"

@dataclass
class Job:
    id: str
    task_name: str
    args: dict
    status: Status = Status.QUEUED
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    progress: float = 0.0              # 0.0 - 1.0
    progress_msg: str = ""
    result: Any = None
    error: Optional[str] = None
    _cancel: threading.Event = field(default_factory=threading.Event, repr=False)

    def cancel(self):
        self._cancel.set()

    def cancelled(self):
        return self._cancel.is_set()

    def set_progress(self, p: float, msg: str = ""):
        self.progress = max(0.0, min(1.0, p))
        self.progress_msg = msg

    def to_dict(self):
        d = asdict(self)
        d.pop("_cancel", None)
        d["status"] = self.status.value
        return d

class _CancelProxy:
    """Passed into the task fn so it can check for cancellation and report progress."""
    def __init__(self, job: Job):
        self._job = job

    def cancelled(self):
        return self._job.cancelled()

    def set_progress(self, p: float, msg: str = ""):
        self._job.set_progress(p, msg)

class JobQueue:
    def __init__(self, max_workers: int = 4):
        self._jobs: Dict[str, Job] = {}
        self._lock = threading.Lock()
        self._q: Queue = Queue()
        self._workers = []
        for i in range(max_workers):
            t = threading.Thread(target=self._worker, name=f"job-worker-{i}", daemon=True)
            t.start()
            self._workers.append(t)

    def submit(self, task_name: str, task_fn: Callable, args: dict) -> Job:
        job = Job(id=uuid.uuid4().hex, task_name=task_name, args=args)
        with self._lock:
            self._jobs[job.id] = job
        self._q.put((task_fn, job))
        logger.info(f"[jobs] submitted {job.id} ({task_name})")
        return job

    def get(self, job_id: str) -> Optional[Job]:
        with self._lock:
            return self._jobs.get(job_id)

    def list(self, limit: int = 20) -> list:
        with self._lock:
            jobs = sorted(self._jobs.values(), key=lambda j: j.created_at, reverse=True)
            return [j.to_dict() for j in jobs[:limit]]

    def cancel(self, job_id: str) -> bool:
        j = self.get(job_id)
        if not j or j.status not in (Status.QUEUED, Status.RUNNING):
            return False
        j.cancel()
        j.status = Status.CANCELLED
        j.finished_at = datetime.utcnow().isoformat()
        return True

    def _worker(self):
        while True:
            task_fn, job = self._q.get()
            try:
                if job.cancelled():
                    continue
                job.status = Status.RUNNING
                job.started_at = datetime.utcnow().isoformat()
                proxy = _CancelProxy(job)
                result = task_fn(**job.args, cancel=proxy)
                if job.cancelled():
                    job.status = Status.CANCELLED
                else:
                    job.status = Status.DONE
                    job.result = result
                    job.progress = 1.0
            except Exception as e:
                job.status = Status.ERROR
                job.error = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
                logger.error(f"[jobs] {job.id} failed: {e}")
            finally:
                job.finished_at = datetime.utcnow().isoformat()
                self._q.task_done()

queue = JobQueue(max_workers=4)
