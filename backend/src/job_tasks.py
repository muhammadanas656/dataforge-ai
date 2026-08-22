"""
Job task registry. Each task is a function taking **args + cancel=_CancelProxy.
"""
from src import eda_engine, reporter

def full_eda(dataset_id: str, cancel=None):
    results = []
    catalog = eda_engine.build_catalog(dataset_id)
    recommended = [a for a in catalog["analyses"] if a["recommended"]][:10]
    for i, a in enumerate(recommended):
        if cancel and cancel.cancelled():
            break
        try:
            r = eda_engine.run_analysis(dataset_id, a["id"], a.get("default_chart"))
            results.append(r)
        except Exception as e:
            results.append({"title": a["title"], "error": str(e), "data": []})
        if cancel:
            cancel.set_progress((i + 1) / len(recommended), f"Running {a['title']}")
    return {"analysis_count": len(results), "results": results}

def generate_report(dataset_id: str, cancel=None):
    return reporter.run_report(dataset_id)

from src import niche_research, competitor_intel, research_automation

def research(niche: str, subreddits=None, avg_price=50, competition=0.5, cancel=None):
    return niche_research.run_research(niche, subreddits=subreddits, avg_price=avg_price, competition=competition, cancel=cancel)

def intel_track(url: str, name: str = "", cancel=None):
    return competitor_intel.track(url=url, name=name, cancel=cancel)

def weekly(run_id: str = "weekly", cancel=None):
    return research_automation.weekly_report(run_id=run_id, cancel=cancel)

REGISTRY = {
    "full_eda": full_eda,
    "generate_report": generate_report,
    "research": research,
    "intel_track": intel_track,
    "weekly": weekly,
}
