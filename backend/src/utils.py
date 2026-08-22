import logging
import os
import re
import json
import ast
from datetime import datetime

def setup_logger(name="dataforge"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    os.makedirs("logs", exist_ok=True)
    fh = logging.FileHandler(f"logs/app_{datetime.now():%Y%m%d}.log", encoding="utf-8")
    ch = logging.StreamHandler()
    fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)
    if not logger.handlers:
        logger.addHandler(fh)
        logger.addHandler(ch)
    return logger

logger = setup_logger()

def repair_and_load_json(text: str, default=None):
    """
    Self-healing JSON parser:
    1. Strips markdown fences (```json ... ```)
    2. Extracts outermost {...} or [...] bounds
    3. Cleans trailing commas (e.g. {"a": 1,})
    4. Falls back to ast.literal_eval for single-quoted Python dicts/lists
    5. Returns default on complete unrecoverable failure
    """
    if not text or not isinstance(text, str):
        return default if default is not None else {}
    
    raw = text.strip()
    
    # 1. Strip markdown fences
    if "```" in raw:
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", raw, re.DOTALL)
        if match:
            raw = match.group(1).strip()
        else:
            raw = raw.replace("```json", "").replace("```", "").strip()

    # 2. Extract outermost bounds
    start_brace = raw.find("{")
    start_bracket = raw.find("[")
    
    if start_brace != -1 and (start_bracket == -1 or start_brace < start_bracket):
        end_brace = raw.rfind("}")
        if end_brace != -1:
            raw = raw[start_brace:end_brace + 1]
    elif start_bracket != -1:
        end_bracket = raw.rfind("]")
        if end_bracket != -1:
            raw = raw[start_bracket:end_bracket + 1]

    # 3. Standard JSON parse attempt
    try:
        return json.loads(raw)
    except Exception:
        pass

    # 4. Regex cleaning: remove trailing commas before closing braces/brackets
    cleaned = re.sub(r",\s*([}\]])", r"\1", raw)
    # Fix unquoted numeric strings like ': 0.95"' -> ': 0.95'
    cleaned = re.sub(r':\s*([0-9.]+)"\s*([,}])', r': \1\2', cleaned)
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # 5. Fallback to ast.literal_eval for single-quoted Python structures
    try:
        # replace JS/JSON booleans and nulls for python evaluation
        py_literal = cleaned.replace("true", "True").replace("false", "False").replace("null", "None")
        res = ast.literal_eval(py_literal)
        if isinstance(res, (dict, list)):
            return res
    except Exception:
        pass

    logger.warning(f"repair_and_load_json failed on text: {text[:120]}... returning default")
    return default if default is not None else {}

KEY_ALIASES = {
    "column": "columns",
    "cols": "columns",
    "analyses": "analyses",
    "analysis": "analyses",
    "steps": "steps",
    "step": "steps",
    "rule": "business_rules",
    "rules": "business_rules",
    "feature": "derived_features",
    "features": "derived_features"
}

def normalize_schema(obj):
    """Recursively normalize known plural/singular schema key discrepancies from LLMs."""
    if isinstance(obj, dict):
        return {KEY_ALIASES.get(k, k): normalize_schema(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalize_schema(x) for x in obj]
    return obj
