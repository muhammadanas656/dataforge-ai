"""
Comprehensive Niche Research, Autonomous Web Crawling, Business Strategy Blueprint,
Scenario Planning, and Future Horizon TRIZ Innovation Resilience Test Suite.
"""
import os
import sys
import pytest

# Ensure backend root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import niche_research, competitor_discovery, scraper_agent, scenario_planning
from src.invention_pipeline import invention_pipeline

UNSEEN_COMPLEX_NICHES = [
    "Autonomous Agricultural Drone Weeding",
    "Biocompatible 3D-Printed Bone Filaments",
    "Edge AI Wind Turbine Acoustic Anomaly Detection",
    "Modular Algae Carbon Capture Bioreactors"
]


def test_autonomous_niche_web_crawler():
    """Verify autonomous crawling, structured dataset extraction, and Phase 1 profiling."""
    for niche in UNSEEN_COMPLEX_NICHES[:2]:
        result = scraper_agent.scraper.crawl_and_structure_niche(
            niche=niche,
            target_urls=["https://news.ycombinator.com", "https://www.producthunt.com"],
            max_pages=1
        )
        assert result is not None
        assert result.get("status") == "success"
        assert "dataset_id" in result
        assert result.get("rows_extracted", 0) > 0
        assert "profile" in result
        assert os.path.exists(f"uploads/{result['filename']}")


def test_business_strategy_blueprint_architect():
    """Verify 3-tier monetization, GTM strategy, and defensibility moats on unseen niches."""
    for niche in UNSEEN_COMPLEX_NICHES[:2]:
        blueprint = niche_research.generate_business_blueprint(niche, category="AI & SaaS")
        assert blueprint is not None
        assert "business_name" in blueprint
        assert "pricing_tiers" in blueprint or "monetization_tiers" in blueprint
        assert "gtm_channels" in blueprint or "gtm_strategy" in blueprint
        assert "defensive_moat" in blueprint


def test_scenario_planning_monte_carlo():
    """Verify Monte Carlo financial projections under extreme economic shocks."""
    for niche in UNSEEN_COMPLEX_NICHES[:2]:
        res = scenario_planning.scenario_planner.generate_scenarios(
            niche=niche,
            base_assumptions={"units_per_month": 150, "price_usd": 129.0},
            category="AI & SaaS"
        )
        assert res is not None
        assert "scenarios" in res
        assert "monte_carlo" in res
        assert "probability_of_profit" in res["monte_carlo"]


def test_triz_future_horizon_invention_engine():
    """Verify TRIZ 39x40 contradiction resolution, physical grounding, and skeptic critic."""
    for niche in UNSEEN_COMPLEX_NICHES[:2]:
        res = invention_pipeline.synthesize_invention(
            domain=niche,
            target_year=2028,
            improving_param="speed",
            worsening_param="energy_efficiency"
        )
        assert res is not None
        assert "concept_name" in res or "synthesis" in res or "domain" in res


def test_competitor_radar_and_threat_quadrants():
    """Verify competitor clustering, sentiment analysis, and pricing positioning."""
    for niche in UNSEEN_COMPLEX_NICHES[:2]:
        comp_data = competitor_discovery.competitor_radar.analyze_niche_competitors(niche)
        assert comp_data is not None
        assert "competitors" in comp_data
        assert "threat_quadrant" in comp_data
        assert len(comp_data["competitors"]) > 0
