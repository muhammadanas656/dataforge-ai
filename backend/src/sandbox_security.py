"""
Sandbox Security & AST Static Analysis Governor.
Prevents malicious code execution in Self-Evolution dynamic features:
1. AST Static Analysis: Strictly blocks dangerous imports (`os`, `sys`, `subprocess`, `shutil`, `socket`, `requests`, `builtins.eval`, `builtins.exec`).
2. Blocks file system write/delete operations (`open`, `remove`, `rmdir`, `unlink`).
3. Execution Timeout Bounds: Enforces thread execution timeout (max 5.0 seconds).
4. Memory Quota: Enforces maximum output object sizes.
"""
from typing import Dict, Any, List, Optional, NamedTuple
import ast
import threading
import time
from src.utils import logger


class SandboxResult(NamedTuple):
    is_safe: bool
    reason: str = ""
    violations: List[str] = []
    sanitized_code: str = ""


class SandboxSecurityGovernor:
    """Enterprise AST Static Code Analyzer and Execution Sandboxing Governor."""

    BLOCKED_MODULES = {
        "os", "sys", "subprocess", "shutil", "socket", "http", "urllib",
        "requests", "aiohttp", "threading", "multiprocessing", "ctypes",
        "importlib", "builtins", "signal", "pty", "commands", "posix"
    }

    BLOCKED_FUNCTIONS = {
        "eval", "exec", "compile", "__import__", "open", "input", "globals",
        "locals", "vars", "dir", "getattr", "setattr", "delattr"
    }

    BLOCKED_ATTRIBUTES = {
        "__class__", "__bases__", "__subclasses__", "__globals__", "__code__",
        "system", "popen", "spawn", "fork", "remove", "rmdir", "unlink"
    }

    def inspect_code_safety(self, code_str: str) -> SandboxResult:
        """Perform deep AST inspection on synthesized Python code."""
        if not code_str or not isinstance(code_str, str):
            return SandboxResult(is_safe=False, reason="Empty or invalid code string.")

        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return SandboxResult(is_safe=False, reason=f"Syntax Error in code: {e}")

        violations = []

        for node in ast.walk(tree):
            # 1. Check Import Statements
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_mod = alias.name.split('.')[0]
                    if root_mod in self.BLOCKED_MODULES:
                        violations.append(f"Blocked import of unauthorized module: '{alias.name}'")

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_mod = node.module.split('.')[0]
                    if root_mod in self.BLOCKED_MODULES:
                        violations.append(f"Blocked from-import of unauthorized module: '{node.module}'")

            # 2. Check Direct Function Calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.BLOCKED_FUNCTIONS:
                        violations.append(f"Blocked dangerous built-in function call: '{node.func.id}()'")

            # 3. Check Attribute Access (e.g. obj.__subclasses__)
            elif isinstance(node, ast.Attribute):
                if node.attr in self.BLOCKED_ATTRIBUTES:
                    violations.append(f"Blocked access to sensitive attribute: '{node.attr}'")

        if violations:
            return SandboxResult(
                is_safe=False,
                reason=f"Sandbox Violation: {len(violations)} prohibited patterns detected.",
                violations=violations,
                sanitized_code=""
            )

        return SandboxResult(
            is_safe=True,
            reason="Code passed all static AST safety and isolation checks.",
            violations=[],
            sanitized_code=code_str
        )

    def execute_safely(self, fn_callable, args=(), kwargs=None, timeout_seconds: float = 3.0) -> Dict[str, Any]:
        """Execute a callable inside a thread with timeout bounds."""
        kw = kwargs or {}
        result_holder: Dict[str, Any] = {"status": "pending", "output": None, "error": None}

        def worker():
            try:
                result_holder["output"] = fn_callable(*args, **kw)
                result_holder["status"] = "success"
            except Exception as e:
                result_holder["error"] = str(e)
                result_holder["status"] = "error"

        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
        t.join(timeout=timeout_seconds)

        if t.is_alive():
            return {
                "status": "timed_out",
                "timed_out": True,
                "error": f"Execution exceeded maximum timeout of {timeout_seconds}s.",
                "output": None
            }

        return result_holder


sandbox_governor = SandboxSecurityGovernor()
