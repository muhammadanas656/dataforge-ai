import os
import re
import ast
import tempfile
import importlib.util
import inspect
from src.plugins import BaseSource, BaseAnalysis

FORBIDDEN_MODULES = {
    "os", "sys", "subprocess", "socket", "shutil", "pty", "commands",
    "builtins", "posix", "nt", "ctypes", "pickle", "shelve", "http.client", "urllib.request"
}

FORBIDDEN_CALLS = {
    "eval", "exec", "open", "__import__", "compile", "globals", "locals"
}

def ast_security_scan(code: str):
    """AST-based static analysis to detect malicious constructs before execution."""
    issues = []
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [f"Syntax error: {e}"]

    for node in ast.walk(tree):
        # Check imports: import os, sys, etc.
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_pkg = alias.name.split(".")[0]
                if root_pkg in FORBIDDEN_MODULES:
                    issues.append(f"Forbidden import: '{alias.name}'")
        # Check from imports: from subprocess import Popen
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_pkg = node.module.split(".")[0]
                if root_pkg in FORBIDDEN_MODULES:
                    issues.append(f"Forbidden import from: '{node.module}'")
        # Check function calls: eval(), exec(), open()
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in FORBIDDEN_CALLS:
                    issues.append(f"Forbidden function call: '{node.func.id}()'")
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr in FORBIDDEN_CALLS:
                    issues.append(f"Forbidden method call: '.{node.func.attr}()'")
    return issues

def static_scan(code: str):
    return ast_security_scan(code)

def syntax_check(code: str):
    try:
        compile(code, "<plugin>", "exec")
        return None
    except SyntaxError as e:
        return str(e)

def smoke_test(code: str, sample_df=None, profile=None):
    issues = static_scan(code)
    if issues:
        return {"ok": False, "issues": issues}
        
    err = syntax_check(code)
    if err:
        return {"ok": False, "issues": [f"Syntax error: {err}"]}
        
    tmp = tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8")
    tmp.write(code)
    tmp.close()
    
    try:
        spec = importlib.util.spec_from_file_location("plugin_under_test", tmp.name)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        found = []
        for _, cls in inspect.getmembers(mod, inspect.isclass):
            if cls.__module__ != "plugin_under_test":
                continue
            if issubclass(cls, BaseAnalysis) and cls is not BaseAnalysis:
                inst = cls()
                ran = False
                if sample_df is not None:
                    res = inst.run(sample_df)
                    ran = res is not None
                found.append({"type": "analysis", "name": getattr(inst, "name", "unknown"), "ran": ran})
            elif issubclass(cls, BaseSource) and cls is not BaseSource:
                found.append({"type": "source", "name": getattr(cls(), "name", "unknown")})
        return {"ok": True, "issues": [], "found": found}
    except Exception as e:
        return {"ok": False, "issues": [f"Runtime execution error: {e}"]}
    finally:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)

def register(name: str, code: str):
    # Pre-validate before writing to disk
    test_res = smoke_test(code)
    if not test_res.get("ok"):
        raise ValueError(f"Plugin failed security smoke test: {test_res.get('issues')}")

    os.makedirs("plugins", exist_ok=True)
    clean_name = re.sub(r"[^a-zA-Z0-9_]", "", name.replace(".py", "")).strip()
    if not clean_name:
        raise ValueError("Invalid plugin name.")
    path = f"plugins/{clean_name}.py"
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    return path
