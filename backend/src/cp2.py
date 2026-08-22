import json
import os
from src.utils import logger, repair_and_load_json
from src.llm import tracked_chat
from src.token_tracker import tracker
from src.rag_cache import ColumnCache
from src.playbooks import get_playbook
from src.frugal import FrugalRouter, frugal_describe

COL_SYSTEM_PROMPT = """You are a data dictionary author. For ONE column, given its name,
kind, MASKED sample values, and stats, respond with ONLY valid JSON:
{
  "semantic_type": "<identifier|categorical|numeric_continuous|numeric_discrete|currency|date|free_text|contact_info>",
  "meaning": "<one-line plain description of what this column represents>",
  "pii": <true|false>,
  "suggested_use": "<identifier|dimension|measure|feature|target>",
  "confidence": <0.0-1.0>
}
Base every claim on the provided evidence. Never invent."""

from src.adaptive_delegation import delegate, learn_from_interaction
from src.model_resilience import get_prompt_template, get_learning_rate
from src.deterministic_fallbacks import fallback_semantic_type

def describe_column(run_id, col, domain="generic"):
    input_data = {
        "name": col["name"],
        "dtype": col.get("dtype", "unknown"),
        "kind": col.get("kind", "unknown"),
        "samples": col.get("sample_values", [])[:5],
        "domain": domain
    }
    
    # 1. Try Adaptive Delegation Router (Knowledge Graph, Distilled Model, RAG Cache)
    result, source, confidence = delegate("semantic_type", input_data, {"domain": domain}, run_id)
    if source != "llm_needed" and result:
        return {
            "name": col["name"],
            "semantic_type": result,
            "meaning": f"Column '{col['name']}' ({source} inference)",
            "pii": False,
            "suggested_use": "measure" if col.get("kind") == "numeric" else "dimension",
            "confidence": confidence,
            "source": source
        }

    # 2. LLM Consultation (Teacher)
    ctx = {
        "name": col["name"],
        "kind": col.get("kind"),
        "samples": col.get("sample_values", []),
        "stats": col.get("stats")
    }
    sys_prompt = get_prompt_template("cp2_system") or COL_SYSTEM_PROMPT
    fallback = fallback_semantic_type(col)
    try:
        text = tracked_chat(
            run_id, "CP2", "dictionary_author",
            [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": json.dumps(ctx, ensure_ascii=False)}
            ],
            temperature=0.1,
            max_completion_tokens=500
        )
        res = repair_and_load_json(text, default=fallback)
    except Exception as e:
        logger.warning(f"[cp2] LLM describe fallback for col '{col.get('name')}': {e}")
        res = fallback
    
    # 3. Learn from this interaction
    sem_type = res.get("semantic_type", "categorical")
    rate = get_learning_rate()
    learn_from_interaction("semantic_type", input_data, sem_type, source="llm", confidence=0.9 * rate)
    return res

def run_cp2(profile_path):
    with open(profile_path, encoding="utf-8") as f:
        profile = json.load(f)
    dataset_id = profile["dataset_id"]

    # Read CP1 domain
    cp1_path = profile_path.replace("profile_", "cp1_")
    domain = "generic"
    try:
        if os.path.exists(cp1_path):
            domain = json.load(open(cp1_path, encoding="utf-8")).get("domain", "generic")
    except Exception as e:
        logger.warning(f"No CP1 file or parse error ({e}); using generic domain")

    cache = ColumnCache()
    router = FrugalRouter(threshold=0.8)
    dictionary = []

    for col in profile.get("columns", []):
        def llm_wrapper(c):
            return describe_column(dataset_id, c)
            
        entry = frugal_describe(col, cache, llm_wrapper, router)
        if entry.get("tier") == "T2_rag":
            tracker.record_cache_hit(dataset_id, "CP2", "rag_cache", "cached", saved=150)
            
        dictionary.append(entry)

    logger.info(f"Frugal tier usage for {dataset_id}: {dict(router.stats)}")
    playbook = get_playbook(domain)

    out = {
        "dataset_id": dataset_id,
        "domain": domain,
        "dictionary": dictionary,
        "playbook": playbook,
        "frugal_tier_stats": dict(router.stats)
    }
    os.makedirs("reports", exist_ok=True)
    path = f"reports/dictionary_{dataset_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"\n=== CP2: DATA DICTIONARY (domain={domain}) ===")
    for e in dictionary:
        sem = e.get('semantic_type', 'unknown')
        use = e.get('suggested_use', 'unknown')
        tier = e.get('tier', 'T3_llm')
        print(f"  {e['name']:20s} [{sem:20s}] use={use:10s} tier={tier}")
    print(f"\n  Frugal tier usage: {dict(router.stats)}")
    print(f"  playbook KPIs: {playbook['kpis']}")
    return out

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "reports/profile_feab58be.json"
    run_cp2(path)
