import json
import os
import pandas as pd
from src.utils import logger

class LoadResult:
    def __init__(self, df, source_name, metadata=None, warnings=None):
        self.df = df
        self.source_name = source_name
        self.metadata = metadata or {}
        self.warnings = warnings or []

class BaseSource:
    name = "base"
    extensions = []
    def can_handle(self, path):
        raise NotImplementedError
    def load(self, path, encoding=None):
        raise NotImplementedError

class CSVSource(BaseSource):
    name = "csv"
    extensions = [".csv", ".tsv"]
    def can_handle(self, p):
        return p.lower().endswith((".csv", ".tsv"))
    def load(self, p, encoding=None):
        sep = "\t" if p.lower().endswith(".tsv") else ","
        df = pd.read_csv(p, sep=sep, encoding=encoding or "utf-8", on_bad_lines="skip")
        return LoadResult(df, self.name, {"separator": sep})

class JSONSource(BaseSource):
    name = "json"
    extensions = [".json"]
    def can_handle(self, p):
        return p.lower().endswith(".json")
    def load(self, p, encoding=None):
        with open(p, "r", encoding=encoding or "utf-8") as f:
            data = json.load(f)
        if isinstance(data, list) and all(isinstance(x, dict) for x in data):
            df = pd.json_normalize(data)
        elif isinstance(data, list):
            df = pd.DataFrame({"value": data})
        elif isinstance(data, dict):
            df = pd.json_normalize([data])
        else:
            raise ValueError("Unsupported JSON structure")
        return LoadResult(df, self.name)

class ExcelSource(BaseSource):
    name = "excel"
    extensions = [".xlsx", ".xls"]
    def can_handle(self, p):
        return p.lower().endswith((".xlsx", ".xls"))
    def load(self, p, encoding=None):
        xl = pd.ExcelFile(p)
        df = xl.parse(xl.sheet_names[0])
        return LoadResult(df, self.name, {"sheets": xl.sheet_names})

class ParquetSource(BaseSource):
    name = "parquet"
    extensions = [".parquet"]
    def can_handle(self, p):
        return p.lower().endswith(".parquet")
    def load(self, p, encoding=None):
        return LoadResult(pd.read_parquet(p), self.name)

SOURCES = [CSVSource(), JSONSource(), ExcelSource(), ParquetSource()]

def detect_and_load(path, encoding=None):
    for s in SOURCES:
        if s.can_handle(path):
            logger.info(f"Detected source: {s.name}")
            return s.load(path, encoding=encoding)
    raise ValueError(f"No source can handle {path}")

import unicodedata
import re

def deep_clean_text(val):
    """Collapse zero-width spaces, RTL marks, BOM, NBSP, and compat whitespace."""
    if pd.isna(val) or not isinstance(val, str):
        return val
    val = re.sub(r"[\u200b-\u200f\ufeff\u00ad]", "", val)
    val = unicodedata.normalize("NFKC", val)  # NFKC folds invisible/compat chars
    return val.strip()

from src import coercion

def canonicalize(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    df = coercion.ensure_unique_columns(df)
    for col in list(df.columns):
        if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].map(deep_clean_text)
            coerced, kind, _ = coercion.coerce_series(df[col])
            if kind:
                df[col] = coerced
    return df.reset_index(drop=True)

def save_snapshot(df, dataset_id, dir="data/canonical"):
    os.makedirs(dir, exist_ok=True)
    pq, csv = f"{dir}/{dataset_id}.parquet", f"{dir}/{dataset_id}.csv"
    df.to_parquet(pq, index=False)
    df.to_csv(csv, index=False)
    return pq, csv
