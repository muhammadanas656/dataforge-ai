"""
Production Pipeline Code Exporter.
Translates governed cleaning plans into standalone, production-ready Python, SQL (dbt), and Airflow DAGs.
"""
import os
import json
from typing import Dict, Any, List
from src.utils import logger

def export_pipeline_code(dataset_id: str) -> Dict[str, Any]:
    """Generate production Python, SQL, and Airflow orchestrator code for a dataset."""
    exec_path = f"reports/execution_{dataset_id}.json"
    plan_path = f"reports/cleaning_plan_{dataset_id}.json"
    if not os.path.exists(plan_path):
        plan_path = f"reports/plan_{dataset_id}.json"
        
    steps: List[Dict[str, Any]] = []
    if os.path.exists(exec_path):
        try:
            with open(exec_path, "r", encoding="utf-8") as f:
                edata = json.load(f)
            steps = edata.get("steps_executed", [])
        except Exception:
            pass
            
    if not steps and os.path.exists(plan_path):
        try:
            with open(plan_path, "r", encoding="utf-8") as f:
                pdata = json.load(f)
            steps = pdata.get("steps", [])
        except Exception:
            pass

    # 1. Standalone Python (Pandas) Script
    python_lines = [
        "#!/usr/bin/env python3",
        '"""',
        f"DataForge AI — Automated Cleaning Pipeline for Dataset: {dataset_id}",
        "Generated automatically. Run standalone without external dependencies.",
        '"""',
        "import pandas as pd",
        "import numpy as np",
        "",
        "def clean_dataset(input_csv_path: str, output_csv_path: str = 'cleaned_data.csv') -> pd.DataFrame:",
        "    print(f'[pipeline] Loading raw dataset: {input_csv_path}')",
        "    df = pd.read_csv(input_csv_path)",
        f"    print(f'[pipeline] Initial shape: {{df.shape[0]}} rows, {{df.shape[1]}} columns')",
        ""
    ]
    
    # Generate Python Transformation Steps
    for i, step in enumerate(steps, 1):
        op = step.get("operation") or step.get("action", "")
        col = step.get("target_column") or step.get("column", "")
        params = step.get("parameters", {})
        
        if op == "standardize_text" and col:
            python_lines.append(f"    # Step {i}: Standardize text formatting for '{col}'")
            python_lines.append(f"    if '{col}' in df.columns:")
            python_lines.append(f"        df['{col}'] = df['{col}'].astype(str).str.strip().str.title()")
        elif op == "fill_nulls" and col:
            fill_val = params.get("value")
            strategy = params.get("strategy", "median")
            python_lines.append(f"    # Step {i}: Impute missing values for '{col}' ({strategy})")
            python_lines.append(f"    if '{col}' in df.columns:")
            if strategy == "median":
                python_lines.append(f"        df['{col}'] = df['{col}'].fillna(df['{col}'].median())")
            elif strategy == "mode":
                python_lines.append(f"        df['{col}'] = df['{col}'].fillna(df['{col}'].mode()[0] if not df['{col}'].mode().empty else 'Unknown')")
            else:
                python_lines.append(f"        df['{col}'] = df['{col}'].fillna({repr(fill_val if fill_val is not None else 'Unknown')})")
        elif op == "remove_outliers" and col:
            python_lines.append(f"    # Step {i}: Clip / filter statistical outliers for '{col}'")
            python_lines.append(f"    if '{col}' in df.columns and pd.api.types.is_numeric_dtype(df['{col}']):")
            python_lines.append(f"        q_low, q_high = df['{col}'].quantile(0.01), df['{col}'].quantile(0.99)")
            python_lines.append(f"        df = df[(df['{col}'] >= q_low) & (df['{col}'] <= q_high)]")
        elif op == "drop_null_rows" and col:
            python_lines.append(f"    # Step {i}: Drop unrecoverable null records for '{col}'")
            python_lines.append(f"    if '{col}' in df.columns:")
            python_lines.append(f"        df = df.dropna(subset=['{col}'])")
        elif op == "drop_duplicates":
            python_lines.append(f"    # Step {i}: Deduplicate identical records")
            python_lines.append(f"    df = df.drop_duplicates()")
        else:
            python_lines.append(f"    # Step {i}: Applied operation '{op}' on target '{col}'")
        python_lines.append("")

    python_lines.extend([
        f"    print(f'[pipeline] Cleaned shape: {{df.shape[0]}} rows, {{df.shape[1]}} columns')",
        "    df.to_csv(output_csv_path, index=False)",
        "    print(f'[pipeline] Saved cleaned output to: {output_csv_path}')",
        "    return df",
        "",
        "if __name__ == '__main__':",
        "    import sys",
        "    input_path = sys.argv[1] if len(sys.argv) > 1 else 'raw_data.csv'",
        "    clean_dataset(input_path)"
    ])
    python_code = "\n".join(python_lines)

    # 2. SQL / dbt Transformation Model
    sql_lines = [
        "-- DataForge AI — Automated SQL Transformation Model (dbt compatible)",
        f"-- Dataset ID: {dataset_id}",
        "",
        "WITH raw_source AS (",
        "    SELECT * FROM {{ source('raw_data', 'incoming_batch') }}",
        "),",
        "cleaned_stage AS (",
        "    SELECT",
    ]
    
    col_exprs = []
    seen_cols = set()
    for step in steps:
        col = step.get("target_column") or step.get("column", "")
        op = step.get("operation") or step.get("action", "")
        if col and col not in seen_cols:
            seen_cols.add(col)
            if op == "standardize_text":
                col_exprs.append(f"        INITCAP(TRIM(CAST({col} AS VARCHAR))) AS {col}")
            elif op == "fill_nulls":
                col_exprs.append(f"        COALESCE({col}, 'Unknown') AS {col}")
            else:
                col_exprs.append(f"        {col}")
    
    if not col_exprs:
        col_exprs.append("        *")
    sql_lines.append(",\n".join(col_exprs))
    sql_lines.extend([
        "    FROM raw_source",
        ")",
        "SELECT * FROM cleaned_stage;"
    ])
    sql_code = "\n".join(sql_lines)

    # 3. Apache Airflow / Prefect DAG
    airflow_lines = [
        "from datetime import datetime, timedelta",
        "from airflow import DAG",
        "from airflow.operators.python import PythonOperator",
        "",
        "default_args = {",
        "    'owner': 'dataforge_ai',",
        "    'depends_on_past': False,",
        "    'start_date': datetime(2026, 1, 1),",
        "    'retries': 2,",
        "    'retry_delay': timedelta(minutes=5),",
        "}",
        "",
        f"dag = DAG(",
        f"    'dataforge_clean_{dataset_id}',",
        "    default_args=default_args,",
        "    description='Autonomous DataForge AI Governed Cleaning Job',",
        "    schedule_interval='@daily',",
        "    catchup=False",
        ")",
        "",
        "def execute_dataforge_cleaning():",
        "    from pipeline import clean_dataset",
        "    clean_dataset('/opt/airflow/data/incoming.csv', '/opt/airflow/data/canonical.csv')",
        "",
        "clean_task = PythonOperator(",
        "    task_id='run_dataforge_cleaning',",
        "    python_callable=execute_dataforge_cleaning,",
        "    dag=dag",
        ")"
    ]
    airflow_dag = "\n".join(airflow_lines)

    return {
        "dataset_id": dataset_id,
        "steps_count": len(steps),
        "python_script": python_code,
        "sql_model": sql_code,
        "airflow_dag": airflow_dag
    }
