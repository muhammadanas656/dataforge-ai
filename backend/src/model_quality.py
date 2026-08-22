"""Probes LLM capability and classifies into quality tiers."""
import json
import os
import time
from datetime import datetime
from src.llm import tracked_chat
from src.utils import logger

TIER_CACHE = "data/model_tier.json"

PROBE_TASKS = [
    {
        "name": "json_strictness",
        "prompt": 'Return ONLY this JSON, nothing else: {"status": "ok", "count": 42}',
        "validate": lambda out: '"status"' in out and '"count"' in out,
        "weight": 1.0
    },
    {
        "name": "logical_reasoning",
        "prompt": "If all cats are animals and some animals are pets, are all cats definitely pets? Answer with one word: yes or no.",
        "validate": lambda out: "no" in out.lower().split()[0] if out.strip() else False,
        "weight": 1.0
    },
    {
        "name": "constraint_following",
        "prompt": "List exactly 3 colors. Output ONLY the color names, comma-separated, nothing else.",
        "validate": lambda out: out.count(",") >= 2 and len(out.split(",")) == 3,
        "weight": 0.8
    },
    {
        "name": "numeric_accuracy",
        "prompt": "What is 15% of 240? Answer with just the number.",
        "validate": lambda out: "36" in out,
        "weight": 1.2
    },
    {
        "name": "domain_knowledge",
        "prompt": "In e-commerce, what does 'SKU' stand for? Answer in 5 words or fewer.",
        "validate": lambda out: "stock" in out.lower() and "unit" in out.lower(),
        "weight": 0.8
    }
]


def probe_model(run_id="probe"):
    """Run capability probes and classify model quality."""
    results = {}
    start_time = time.time()

    for task in PROBE_TASKS:
        try:
            t0 = time.time()
            response = tracked_chat(
                run_id, "PROBE", "quality",
                [{"role": "user", "content": task["prompt"]}],
                temperature=0,
                max_completion_tokens=50
            )
            latency = time.time() - t0
            passed = task["validate"](response.strip())
            results[task["name"]] = {
                "passed": passed,
                "latency": round(latency, 2),
                "response": response[:100]
            }
        except Exception as e:
            results[task["name"]] = {
                "passed": False,
                "latency": 0,
                "error": str(e)
            }

    total_time = time.time() - start_time
    score = sum(
        task["weight"] for task in PROBE_TASKS
        if results.get(task["name"], {}).get("passed", False)
    )
    max_score = sum(t["weight"] for t in PROBE_TASKS)

    if score >= max_score * 0.8:
        tier = "high"
    elif score >= max_score * 0.5:
        tier = "mid"
    else:
        tier = "low"

    result = {
        "tier": tier,
        "score": round(score, 2),
        "max_score": max_score,
        "percentage": round(score / max_score * 100, 1),
        "total_probe_time": round(total_time, 2),
        "results": results,
        "probed_at": datetime.now().isoformat()
    }

    os.makedirs("data", exist_ok=True)
    with open(TIER_CACHE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    logger.info(f"[model_quality] Probed model: tier={tier}, score={score}/{max_score}")
    return result


def get_cached_tier():
    if os.path.exists(TIER_CACHE):
        try:
            return json.load(open(TIER_CACHE, encoding="utf-8"))
        except Exception:
            pass
    return None


def get_tier():
    cached = get_cached_tier()
    if cached:
        return cached["tier"]
    return "mid"


import threading

_probing_lock = threading.Lock()
_is_probing = False


def get_tier_async():
    """Returns cached tier immediately. Probes in background if missing."""
    global _is_probing
    cached = get_cached_tier()
    if cached:
        return cached["tier"]

    with _probing_lock:
        if not _is_probing:
            _is_probing = True

            def _background_probe():
                global _is_probing
                try:
                    probe_model()
                finally:
                    _is_probing = False

            threading.Thread(target=_background_probe, daemon=True).start()

    return "mid"
