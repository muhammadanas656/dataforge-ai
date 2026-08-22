import pytest
from src.reddit_cache import RedditCache

def test_reddit_cache_set_and_get(tmp_path):
    cache = RedditCache(cache_dir=str(tmp_path))
    posts = [{"id": "p1", "title": "Great tool", "sentiment": 0.8}]
    
    assert cache.get("ergonomic keyboards") is None
    cache.set("ergonomic keyboards", posts)
    cached = cache.get("ergonomic keyboards")
    assert cached is not None
    assert len(cached) == 1
    assert cached[0]["id"] == "p1"

def test_reddit_cache_stats_and_clear(tmp_path):
    cache = RedditCache(cache_dir=str(tmp_path))
    cache.set("idea1", [{"title": "Post 1"}])
    cache.set("idea2", [{"title": "Post 2"}])
    
    stats = cache.stats()
    assert stats["total_entries"] == 2
    
    cache.clear()
    stats_after = cache.stats()
    assert stats_after["total_entries"] == 0
