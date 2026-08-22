"""Caching layer for Reddit API calls to prevent rate limiting and redundant requests."""
import json
import os
import time
from datetime import datetime, timedelta
from src.utils import logger

CACHE_DIR = "data/reddit_cache"
DEFAULT_TTL = 3600 * 6  # 6 hours

class RedditCache:
    def __init__(self, cache_dir=CACHE_DIR):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _cache_key(self, query: str, subreddit: str = "all") -> str:
        """Generate a stable cache key for a query."""
        import hashlib
        key = f"{subreddit}:{query.lower().strip()}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def _cache_path(self, cache_key: str) -> str:
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, query: str, subreddit: str = "all", max_age_seconds: int = DEFAULT_TTL):
        """Retrieve cached posts if fresh enough."""
        cache_key = self._cache_key(query, subreddit)
        path = self._cache_path(cache_key)
        
        if not os.path.exists(path):
            return None
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            
            cached_time = datetime.fromisoformat(cached['timestamp'])
            age_seconds = (datetime.now() - cached_time).total_seconds()
            
            if age_seconds > max_age_seconds:
                logger.info(f"[reddit_cache] Cache expired for '{query}' ({age_seconds:.0f}s old)")
                return None
            
            logger.info(f"[reddit_cache] Cache hit for '{query}' ({age_seconds:.0f}s old)")
            return cached['posts']
        
        except Exception as e:
            logger.warning(f"[reddit_cache] Failed to read cache: {e}")
            return None
    
    def set(self, query: str, posts: list, subreddit: str = "all"):
        """Store posts in cache with timestamp."""
        cache_key = self._cache_key(query, subreddit)
        path = self._cache_path(cache_key)
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'query': query,
                    'subreddit': subreddit,
                    'posts': posts,
                    'count': len(posts)
                }, f, indent=2)
            logger.info(f"[reddit_cache] Cached {len(posts)} posts for '{query}'")
        except Exception as e:
            logger.warning(f"[reddit_cache] Failed to write cache: {e}")
    
    def clear(self):
        """Clear all cached data."""
        import shutil
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.info("[reddit_cache] Cleared all cached data")
    
    def stats(self):
        """Return cache statistics."""
        if not os.path.exists(self.cache_dir):
            return {"total_entries": 0, "total_size_mb": 0}
        
        files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
        total_size = sum(os.path.getsize(os.path.join(self.cache_dir, f)) for f in files)
        
        return {
            "total_entries": len(files),
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }

reddit_cache = RedditCache()
