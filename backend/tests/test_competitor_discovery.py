import pytest
from src.competitor_discovery import CompetitorDiscovery

def test_competitor_discovery_seeds():
    cd = CompetitorDiscovery()
    competitors = cd._suggest_competitors_via_llm("Ergonomic Split Keyboard")
    assert isinstance(competitors, list)
    assert len(competitors) >= 2
    assert "name" in competitors[0]

def test_competitor_discovery_caching():
    cd = CompetitorDiscovery()
    comps = cd.discover_competitors("Ergonomic Split Keyboard", max_competitors=2)
    assert isinstance(comps, list)
    assert len(comps) >= 1
    assert "pricing" in comps[0]
