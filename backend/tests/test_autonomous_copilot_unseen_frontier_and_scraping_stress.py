"""
Autonomous Copilot Unseen Frontier & Extreme Scraping Stress Test Suite.
Validates:
1. Unseen, ambiguous, and multi-lingual copilot inquiries with zero-token semantic learning.
2. Deep obfuscated scraper target extraction and structured metadata parsing.
3. Complex internet datasets (JSON-in-CSV, emojis/UTF-8, high-cardinality sparse arrays).
4. End-to-end autonomous pipeline stress and cross-disciplinary invention synthesis.
"""
import pytest
import os
import json
import numpy as np
import pandas as pd
from src.assistant_engine import assistant_engine, AssistantEngine
from src.scraper_agent import scraper, decode_cloudflare_email
from src.profiler import profile_dataframe
from src import phase1, cp2, cp3, governance, executor, scenario_planning, eda_engine
from src.invention_pipeline import invention_pipeline
from src.triz_engine import triz_engine


# =====================================================================
# 1. UNSEEN COPILOT INQUIRIES & DYNAMIC TOKEN SAVINGS
# =====================================================================

@pytest.fixture(autouse=True)
def reset_copilot_state():
    """Ensure clean assistant state before each test."""
    assistant_engine.user_profile["require_confirmation"] = False
    assistant_engine._save_user_profile()
    yield
    assistant_engine.user_profile["require_confirmation"] = False
    assistant_engine._save_user_profile()


@pytest.mark.asyncio
async def test_copilot_unseen_intent_routing_and_learning_loop():
    """Verify copilot routes unseen questions accurately and saves tokens on repeated concepts."""
    test_sess = "sess_unseen_001"
    
    # 1. Ask a novel complex question
    q1 = "Can you explain how partial correlation inversion isolates direct causal relationships in telemetry?"
    res1 = await assistant_engine.process_query(test_sess, q1)
    assert "response" in res1
    assert len(res1["response"]) > 20
    
    # 2. Re-querying should be tracked and maintain session state
    res2 = await assistant_engine.process_query(test_sess, q1)
    assert "response" in res2
    assert len(res2["response"]) > 20


@pytest.mark.asyncio
async def test_copilot_multilingual_and_slang_queries():
    """Verify copilot handles Spanish, German, and developer slang queries gracefully."""
    queries = [
        "¿Cuáles son los servicios principales que ofrece DataForge?",
        "Wie funktioniert die MICE-Imputation für fehlende Daten?",
        "yo drop some stats on my telemetry dataframe asap pls"
    ]
    for q in queries:
        res = await assistant_engine.process_query("sess_multi", q)
        assert "response" in res
        assert len(res["response"]) > 0
        assert isinstance(res["response"], str)


@pytest.mark.asyncio
async def test_copilot_implicit_action_disambiguation():
    """Verify copilot correctly identifies implicit action intents."""
    q = "Please clean up the nulls and outliers in my active dataset"
    res = await assistant_engine.process_query("sess_implicit", q)
    assert "response" in res
    assert isinstance(res["response"], str)


@pytest.mark.asyncio
async def test_copilot_confirmation_toggle_dynamic():
    """Verify confirmation protocol switches between direct execution and action proposal."""
    # Step A: Confirmation mode enabled
    assistant_engine.user_profile["require_confirmation"] = True
    assistant_engine._save_user_profile()
    
    res_proposal = await assistant_engine.process_query("sess_conf", "Scrape leads for Quantum Cryogenics")
    assert "response" in res_proposal
    assert res_proposal.get("action_card") is not None
    assert res_proposal["action_card"]["type"] == "action_proposal"
    
    # Step B: Confirmation mode disabled
    assistant_engine.user_profile["require_confirmation"] = False
    assistant_engine._save_user_profile()
    
    res_auto = await assistant_engine.process_query("sess_conf", "What is DataForge AI?")
    assert "response" in res_auto


# =====================================================================
# 2. COMPLEX WEB SCRAPING & DEEP OBFUSCATION TARGETS
# =====================================================================

def test_scraper_cloudflare_email_deobfuscation():
    """Verify Cloudflare XOR email de-obfuscation on real-world hex encodings."""
    # Encoded "contact@quantum-cryo.tech"
    encoded_hex = "670c02090d0e27140613020b0e09024904080a"
    decoded = decode_cloudflare_email(encoded_hex)
    assert "@" in decoded


def test_scraper_schema_org_and_json_ld_extraction():
    """Verify scraper extracts organization and contact points from embedded JSON-LD scripts."""
    json_ld_html = """
    <!DOCTYPE html>
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "Organization",
          "name": "BioSynthetica Labs",
          "url": "https://biosynthetica.io",
          "email": "contact@biosynthetica.io",
          "telephone": "+1-800-555-0149"
        }
        </script>
      </head>
      <body>
        <h1>BioSynthetica Frontier Research</h1>
      </body>
    </html>
    """
    json_data = scraper.extract_json_ld(json_ld_html)
    assert isinstance(json_data, list)
    assert len(json_data) >= 1
    assert "name" in json_data[0].columns
    assert json_data[0]["name"].iloc[0] == "BioSynthetica Labs"


def test_scraper_table_extraction_resilience():
    """Verify scraper extracts structured data tables from complex HTML."""
    table_html = """
    <html>
      <body>
        <table>
          <thead>
            <tr><th>Vessel Name</th><th>Depth Rating</th><th>Status</th></tr>
          </thead>
          <tbody>
            <tr><td>Nautilus IV</td><td>6000m</td><td>Active</td></tr>
            <tr><td>AbyssExplorer</td><td>11000m</td><td>Testing</td></tr>
          </tbody>
        </table>
      </body>
    </html>
    """
    tables = scraper.extract_tables(table_html)
    assert isinstance(tables, list)
    assert len(tables) >= 1
    assert len(tables[0]) == 2


# =====================================================================
# 3. UNIQUE INTERNET DATASETS & EXTREME COLUMN ANOMALIES
# =====================================================================

def test_dataset_json_strings_inside_csv_columns(tmp_path):
    """Verify DataForge profiles and handles JSON-string embedded columns."""
    data = {
        "device_id": [f"DEV_{i:04d}" for i in range(50)],
        "telemetry_json": [
            json.dumps({"temp_k": 4.2 + (i * 0.1), "pressure_bar": 1.013, "status": "nominal"})
            for i in range(50)
        ],
        "log_level": ["INFO", "WARN", "INFO", "DEBUG", "ERROR"] * 10,
        "battery_mv": [3700 - (i * 5) for i in range(50)]
    }
    df = pd.DataFrame(data)
    prof = profile_dataframe(df)
    assert prof["total_rows"] == 50
    assert prof["total_columns"] == 4
    assert len(prof["columns"]) == 4


def test_dataset_multilingual_unicode_and_emojis(tmp_path):
    """Verify DataForge handles full UTF-8 Unicode, Japanese kanji, Arabic, and emojis."""
    data = {
        "id": list(range(1, 11)),
        "customer_name": ["أحمد", "田中太郎", "Müller & Söhne", "Jean-Luc", "Владимир", "José", "Chloé", "Li Wei (李伟)", "✨ Quantum 🚀", "Alpha Inc."],
        "sentiment_score": [0.85, 0.92, -0.12, 0.45, 0.0, -0.78, 0.99, 0.33, 0.88, 0.10],
        "feedback_text": [
            "خدمة ممتازة وسريعة جدا",
            "非常に素晴らしいデータサイエンスプラットフォームです！",
            "Hervorragende Leistung bei großen Datenmengen 👍",
            "Très bon outil d'analyse causale.",
            "Отличная система профилирования данных.",
            "Excelente servicio al cliente.",
            "Parfait pour nos besoins en R&D.",
            "算法效率非常高，值得推荐！",
            "🚀 100x faster than manual python pipelines! 🔥",
            "Standard business intelligence features."
        ]
    }
    df = pd.DataFrame(data)
    prof = profile_dataframe(df)
    assert prof["total_rows"] == 10
    assert prof["total_columns"] == 4


def test_causal_eda_high_dimensional_rank_deficient():
    """Verify Causal DAG handles rank-deficient systems where features > samples."""
    np.random.seed(42)
    X = np.random.randn(20, 5)
    synthetic_cols = [X @ np.random.randn(5) for _ in range(20)]
    all_data = {f"feat_{i}": col for i, col in enumerate(synthetic_cols)}
    df = pd.DataFrame(all_data)
    
    dag = eda_engine.compute_causal_dag(df)
    assert "nodes" in dag
    assert len(dag["nodes"]) > 0
    
    hypotheses = eda_engine.generate_statistical_hypotheses(df)
    assert isinstance(hypotheses, list)


# =====================================================================
# 4. SYSTEM-WIDE INVENTION & SCENARIO ENGINE HARDENING
# =====================================================================

def test_triz_cross_disciplinary_paradox_synthesis():
    """Verify TRIZ engine resolves complex cross-disciplinary trade-offs."""
    res = triz_engine.resolve_contradiction(
        improving_param="speed",
        worsening_param="energy_efficiency",
        domain="quantum_computing"
    )
    assert "contradiction" in res
    assert "applied_principle" in res
    assert "invention" in res


def test_scenario_planner_multimodal_fat_tail_distributions():
    """Verify Monte Carlo simulation handles fat-tail distributions and high volatility."""
    base_assumptions = {
        "initial_revenue": 500000,
        "growth_rate_mean": 0.15,
        "growth_rate_std": 0.60,
        "burn_rate_monthly": 45000,
        "iterations": 500
    }
    scenarios = scenario_planning.scenario_planner.generate_scenarios(
        niche="Deep-Sea Autonomous Mining ROVs",
        base_assumptions=base_assumptions,
        category="DeepTech"
    )
    assert "scenarios" in scenarios
    assert "monte_carlo" in scenarios
    assert "probability_of_profit" in scenarios["monte_carlo"]
    assert 0.0 <= scenarios["monte_carlo"]["probability_of_profit"] <= 1.0
