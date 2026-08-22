"""
Workspace tenancy: single source of truth for the active workspace.
Default workspace is "default" — existing single-user usage stays intact.
"""
import os
import re
import contextvars
from typing import Optional
from src.utils import logger

DEFAULT_WORKSPACE = "default"
WORKSPACE_RE = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")

_current_workspace: contextvars.ContextVar[str] = contextvars.ContextVar(
    "workspace", default=DEFAULT_WORKSPACE
)


def get_workspace() -> str:
    return _current_workspace.get()


def set_workspace(workspace_id: str) -> str:
    if not workspace_id:
        workspace_id = DEFAULT_WORKSPACE
    if not WORKSPACE_RE.match(workspace_id):
        raise ValueError(
            f"Invalid workspace_id: {workspace_id!r}. Must match {WORKSPACE_RE.pattern}"
        )
    _current_workspace.set(workspace_id)
    return workspace_id


def reset_workspace(token=None):
    if token is not None:
        _current_workspace.reset(token)
    else:
        _current_workspace.set(DEFAULT_WORKSPACE)


def workspace_root(workspace_id: Optional[str] = None) -> str:
    wid = workspace_id or get_workspace()
    return os.path.join("data", wid)


def workspace_path(relative_path: str, workspace_id: Optional[str] = None) -> str:
    wid = workspace_id or get_workspace()
    base = os.path.abspath(workspace_root(wid))
    full = os.path.abspath(os.path.join(base, relative_path))
    if not full.startswith(base):
        raise ValueError(f"Path traversal rejected: {relative_path}")
    return full


def ensure_workspace_dir(workspace_id: Optional[str] = None) -> str:
    path = workspace_root(workspace_id)
    os.makedirs(path, exist_ok=True)
    return path


def list_workspaces() -> list:
    if not os.path.exists("data"):
        return [DEFAULT_WORKSPACE]
    out = []
    for entry in os.listdir("data"):
        full = os.path.join("data", entry)
        if os.path.isdir(full) and WORKSPACE_RE.match(entry):
            out.append(entry)
    if DEFAULT_WORKSPACE not in out:
        out.append(DEFAULT_WORKSPACE)
    return sorted(out)
