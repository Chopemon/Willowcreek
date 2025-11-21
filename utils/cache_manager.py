# utils/cache_manager.py
"""
Smart caching system for AI responses and expensive computations.
Implements LRU cache with TTL (time-to-live) for temporary data.
"""

import hashlib
import time
from typing import Any, Optional, Dict
from collections import OrderedDict


class SmartCache:
    """
    LRU cache with optional TTL for temporary caching.
    Use for world snapshots, NPC states, and detection results.
    """

    def __init__(self, max_size: int = 100, ttl_seconds: Optional[int] = None):
        """
        Args:
            max_size: Maximum number of items to cache
            ttl_seconds: Time-to-live in seconds. None = no expiration
        """
        self.cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.hits = 0
        self.misses = 0

    def _make_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = str((args, sorted(kwargs.items())))
        return hashlib.md5(key_data.encode()).hexdigest()

    def _is_expired(self, timestamp: float) -> bool:
        """Check if cache entry is expired"""
        if self.ttl_seconds is None:
            return False
        return (time.time() - timestamp) > self.ttl_seconds

    def get(self, *args, **kwargs) -> Optional[Any]:
        """Get cached value if exists and not expired"""
        key = self._make_key(*args, **kwargs)

        if key in self.cache:
            value, timestamp = self.cache[key]

            if self._is_expired(timestamp):
                # Expired - remove and return None
                del self.cache[key]
                self.misses += 1
                return None

            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            return value

        self.misses += 1
        return None

    def set(self, value: Any, *args, **kwargs):
        """Cache a value"""
        key = self._make_key(*args, **kwargs)

        # Remove oldest if at capacity
        if key not in self.cache and len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)  # Remove oldest

        self.cache[key] = (value, time.time())

    def invalidate(self, *args, **kwargs):
        """Remove specific cache entry"""
        key = self._make_key(*args, **kwargs)
        if key in self.cache:
            del self.cache[key]

    def clear(self):
        """Clear entire cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "ttl_seconds": self.ttl_seconds
        }


# Global cache instances
sexual_detection_cache = SmartCache(max_size=200, ttl_seconds=300)  # 5 minute TTL
world_snapshot_cache = SmartCache(max_size=50, ttl_seconds=60)  # 1 minute TTL
npc_state_cache = SmartCache(max_size=100, ttl_seconds=120)  # 2 minute TTL


def print_cache_stats():
    """Print statistics for all caches"""
    print("\n[Cache Statistics]")
    print("─" * 60)
    print("Sexual Detection Cache:", sexual_detection_cache.get_stats())
    print("World Snapshot Cache:", world_snapshot_cache.get_stats())
    print("NPC State Cache:", npc_state_cache.get_stats())
    print("─" * 60)
