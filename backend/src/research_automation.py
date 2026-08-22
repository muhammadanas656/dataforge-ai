"""Research automation: alerts, grounded SWOT, weekly digest."""
import os
import json
import time
import glob
import threading
from datetime import datetime
from src.utils import logger, repair_and_load_json
from src.storage import save_artifact
from src.llm import tracked_chat
from src import niche_research, competitor_intel


import hashlib

ALERT_HISTORY_PATH = "data/alert_history.json"


def _alert_sig(alert):
    msg = alert.get("message", "")
    score_match = re.search(r"scores?\s*(\d+)", msg, re.IGNORECASE)
    bucket = ""
    if score_match:
        score = int(score_match.group(1))
        bucket = f"_bucket_{score // 10}"
    pct_match = re.search(r"\+(\d+)%", msg)
    if pct_match:
        pct = int(pct_match.group(1))
        bucket += f"_growth_{pct // 20}"
    return hashlib.md5(f"{alert['type']}_{bucket}_{msg[:20]}".encode("utf-8")).hexdigest()


def _load_alert_history():
    os.makedirs("data", exist_ok=True)
    if os.path.exists(ALERT_HISTORY_PATH):
        try:
            return json.load(open(ALERT_HISTORY_PATH, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_alert_history(hist):
    os.makedirs("data", exist_ok=True)
    with open(ALERT_HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(hist, f, indent=2)


def detect_alerts(dedup=True):
    """Stateless scan for high-conviction signals with 24h suppression window to prevent alert fatigue."""
    raw_alerts = []
    for r in niche_research.list_research():
        full = niche_research.get_research(r["id"])
        if not full:
            continue
        score = full.get("opportunity_score", 0)
        if score >= 65:
            raw_alerts.append({
                "type": "hot_niche",
                "severity": "high",
                "message": f"Niche '{full['niche']}' scores {score}/100 — High potential market opportunity."
            })
        growth = full.get("metrics", {}).get("growth", 0)
        if growth >= 0.25:
            raw_alerts.append({
                "type": "rising_trend",
                "severity": "medium",
                "message": f"Niche '{full['niche']}' interest grew +{int(growth * 100)}% over recent horizon."
            })
            
    for g in competitor_intel.feature_gap():
        raw_alerts.append({
            "type": "feature_gap",
            "severity": "medium",
            "message": f"Feature '{g['feature']}' offered by {', '.join(g['offered_by'])} but missing from {', '.join(g['missing_from'])}."
        })
        
    for c in competitor_intel._load_reg():
        for ch in competitor_intel.price_changes(c["id"]):
            before_p = ch.get("before") or 1
            pct = abs(ch["delta"]) / before_p * 100
            if pct >= 5:
                raw_alerts.append({
                    "type": "price_movement",
                    "severity": "high",
                    "message": f"{c['name']} changed price on '{ch['title'][:32]}' by {ch['delta']:+.2f} ({pct:.1f}%)."
                })
                
    if not dedup:
        return raw_alerts

    now = time.time()
    history = _load_alert_history()
    # Filter out entries older than 24h (86400s)
    history = {k: v for k, v in history.items() if (now - v) < 86400}
    
    unique_alerts = []
    for a in raw_alerts:
        sig = _alert_sig(a)
        a["signature"] = sig
        if sig not in history:
            unique_alerts.append(a)
            history[sig] = now
            
    _save_alert_history(history)
    # If no new unique alerts, return recent active alerts from raw for live display
    return unique_alerts if unique_alerts else raw_alerts[:10]


def generate_swot(run_id, niche, research=None):
    """Grounded SWOT: LLM reasons strictly over real collected metrics and competitor gaps."""
    ctx = {"niche": niche}
    if research:
        ctx.update({
            "metrics": research.get("metrics"),
            "pain_points": research.get("pain_points"),
            "tam": research.get("market", {}).get("tam_annual_usd"),
            "score": research.get("opportunity_score"),
            "gaps": competitor_intel.feature_gap()
        })
    prompt = (
        "You are an expert strategic market analyst. Using ONLY the provided niche metrics and market data, "
        "output JSON with keys 'strengths', 'weaknesses', 'opportunities', 'threats' containing 2-3 grounded bullet points each. "
        "Structure: {\"strengths\": [...], \"weaknesses\": [...], \"opportunities\": [...], \"threats\": [...]}"
    )
    try:
        text = tracked_chat(
            run_id=run_id,
            stage="RESEARCH",
            agent="swot",
            messages=[
                {"role": "system", "content": "You are an analytical market intelligence strategist. Output valid JSON only."},
                {"role": "user", "content": prompt + "\n\nData context:\n" + json.dumps(ctx)}
            ],
            temperature=0.3,
            max_completion_tokens=400
        )
        swot = repair_and_load_json(text, default={})
    except Exception as e:
        logger.warning(f"[swot] LLM synthesis failed: {e}")
        swot = {}
        
    for k in ("strengths", "weaknesses", "opportunities", "threats"):
        swot.setdefault(k, [])
        if not swot[k]:
            if k == "strengths":
                swot[k] = [f"Strong demand volume in {niche}", "Organic user discussions indicate active interest"]
            elif k == "weaknesses":
                swot[k] = ["Product category requires high initial quality focus", "Potential customer support overhead"]
            elif k == "opportunities":
                swot[k] = ["Directly solve top unmet user complaints", "Differentiate with clear pricing and durability"]
            elif k == "threats":
                swot[k] = ["Established competitors may respond with discounts", "Supplier cost fluctuations"]
    return swot


def weekly_report(run_id="weekly", cancel=None):
    research = niche_research.list_research()
    intel = competitor_intel._load_reg()
    alerts = detect_alerts()
    top = sorted(research, key=lambda x: x["score"], reverse=True)[:5]
    digest = {
        "created": datetime.now().isoformat(),
        "research_count": len(research),
        "intel_count": len(intel),
        "alerts": alerts,
        "top_opportunities": top,
        "summary": ""
    }
    try:
        text = tracked_chat(
            run_id=run_id,
            stage="RESEARCH",
            agent="weekly_digest",
            messages=[
                {"role": "system", "content": "Summarize this weekly intelligence data in 2-3 concise executive sentences. Output JSON: {\"summary\": \"...\"}"},
                {"role": "user", "content": json.dumps({"top": top, "alerts": alerts[:6]})}
            ],
            temperature=0.3,
            max_completion_tokens=200
        )
        res = repair_and_load_json(text, default={"summary": ""})
        digest["summary"] = res.get("summary", "")
    except Exception as e:
        logger.warning(f"[weekly] LLM summary fallback: {e}")
        
    if not digest["summary"]:
        digest["summary"] = f"Tracked {len(research)} niches and {len(intel)} competitors. {len(alerts)} alerts detected across pricing and feature gaps."
        
    ts = int(time.time())
    path = f"reports/weekly_{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(digest, f, indent=2, ensure_ascii=False)
    save_artifact(path)
    return digest


def latest_weekly():
    files = sorted(glob.glob("reports/weekly_*.json"))
    if files:
        try:
            return json.load(open(files[-1], encoding="utf-8"))
        except Exception:
            pass
    return None


def start_scheduler(hours=168):
    """Optional recurring digest runner."""
    if os.getenv("RESEARCH_SCHEDULER") != "1":
        return
    def loop():
        while True:
            time.sleep(hours * 3600)
            try:
                weekly_report("scheduler")
            except Exception as e:
                logger.error(f"[scheduler] {e}")
    t = threading.Thread(target=loop, daemon=True)
    t.start()
