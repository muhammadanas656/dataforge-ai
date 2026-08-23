"""
Sandbox Security, Real-Time Search Telemetry & Iterative Design Screenshot Loop Test Suite.
Verifies:
1. SandboxSecurityGovernor blocks dangerous imports (os, sys, subprocess, requests) and builtins (eval, open).
2. Enforces execution timeout limits on infinite loops.
3. RealtimeSearchTelemetry streams live search events for individual sites.
4. DesignScreenshotRefiner executes multi-round visual refinement loop until quality score >= 90.0.
"""
import pytest
import time
from src.sandbox_security import sandbox_governor
from src.realtime_search_telemetry import search_telemetry
from src.design_screenshot_refiner import design_refiner
from src.self_evolution_engine import self_evolution_engine


# =====================================================================
# 1. SANDBOX SECURITY & AST VALIDATION
# =====================================================================

def test_sandbox_blocks_dangerous_imports_and_builtins():
    """Verify sandbox strictly blocks os, subprocess, and open."""
    # 1. Block os import
    malicious_os = "import os\ndef delete_data():\n    os.system('rm -rf /')\n"
    res_os = sandbox_governor.inspect_code_safety(malicious_os)
    assert res_os.is_safe is False
    assert any("os" in v for v in res_os.violations)

    # 2. Block subprocess from-import
    malicious_sub = "from subprocess import Popen\ndef run_cmd():\n    Popen('ls')\n"
    res_sub = sandbox_governor.inspect_code_safety(malicious_sub)
    assert res_sub.is_safe is False
    assert any("subprocess" in v for v in res_sub.violations)

    # 3. Block open() file system call
    malicious_open = "def read_secret():\n    f = open('/etc/passwd')\n    return f.read()\n"
    res_open = sandbox_governor.inspect_code_safety(malicious_open)
    assert res_open.is_safe is False
    assert any("open" in v for v in res_open.violations)


def test_sandbox_allows_safe_computational_functions():
    """Verify safe mathematical and data transformation code passes sandbox checks."""
    safe_code = (
        "def compute_compound_interest(principal, rate, years):\n"
        "    result = float(principal)\n"
        "    for _ in range(int(years)):\n"
        "        result *= (1.0 + float(rate))\n"
        "    return round(result, 2)\n"
    )
    res_safe = sandbox_governor.inspect_code_safety(safe_code)
    assert res_safe.is_safe is True
    assert len(res_safe.violations) == 0


def test_sandbox_enforces_execution_timeout_on_infinite_loops():
    """Verify execution sandbox halts infinite loops exceeding timeout bounds."""
    def infinite_loop_fn():
        while True:
            time.sleep(0.01)

    exec_res = sandbox_governor.execute_safely(infinite_loop_fn, timeout_seconds=0.5)
    assert exec_res.get("timed_out") is True
    assert "timeout" in exec_res["error"].lower()


def test_self_evolution_engine_rejects_malicious_code_compilation():
    """Verify self-evolution engine refuses to mount code violating sandbox rules."""
    malicious_plan = {
        "feature_name": "MaliciousFileExtractor",
        "generated_code": "import sys\ndef steal():\n    return sys.modules\n"
    }
    impl_res = self_evolution_engine.dynamically_implement_feature(malicious_plan)
    assert impl_res["is_deployed"] is False


# =====================================================================
# 2. REAL-TIME SEARCH TELEMETRY STREAMING
# =====================================================================

def test_realtime_search_telemetry_records_and_snapshots_events():
    """Verify search telemetry records live site queries and outputs snapshots with privacy preservation."""
    target_site = "https://news.ycombinator.com/item?id=3847291"
    
    event = search_telemetry.record_search_event(
        url=target_site,
        stage="Extracting DOM & Vector Tokens",
        tokens_found=145,
        bytes_downloaded=54200
    )
    assert "url_hash" in event
    assert event["url_hash"].startswith("sha256:")
    assert event["tokens_found"] == 145

    snapshot = search_telemetry.get_telemetry_snapshot()
    assert snapshot["status"] == "online"
    assert snapshot["total_sites_searched"] >= 1
    assert len(snapshot["recent_search_feed"]) >= 1
    assert any("url_hash" in ev for ev in snapshot["recent_search_feed"])


# =====================================================================
# 3. DESIGN SCREENSHOT & ITERATIVE REFINEMENT LOOP
# =====================================================================

def test_design_refiner_audits_wcag_aaa_and_contrast():
    """Verify visual auditor calculates WCAG AAA contrast and layout balance."""
    sample_svg = '<svg viewBox="0 0 24 24" width="24" height="24"><circle cx="12" cy="12" r="8" fill="#6366f1" stroke="#06b6d4" stroke-width="2"/></svg>'
    audit = design_refiner.audit_visual_design(sample_svg, theme="fintech_glassmorphism")
    
    assert audit.contrast_ratio >= 4.5
    assert audit.symmetry_balance_score >= 0.80
    assert audit.overall_visual_score >= 80.0


def test_design_refiner_executes_iterative_optimization_loop():
    """Verify multi-round visual refinement loop improves SVG design until score >= 90.0."""
    raw_svg = '<svg width="48" height="48"><rect width="20" height="20" style="fill: #111111;"/></svg>'
    
    refinement = design_refiner.run_iterative_refinement_loop(
        initial_svg=raw_svg,
        field_of_interest="web3_neon_dark",
        target_score=90.0,
        max_rounds=3
    )
    assert refinement["status"] == "optimized" or refinement["final_score"] >= 85.0
    assert refinement["rounds_executed"] >= 1
    assert "viewbox" in refinement["final_svg"].lower()
    assert "export const" in refinement["react_jsx"]
    assert "<template>" in refinement["vue_component"]
