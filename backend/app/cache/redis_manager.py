"""Redis cache manager with connection handling and decorators"""
import json
import os
from typing import Any, Optional, Callable
from functools import wraps
import logging

try:
    import redis
    from redis.exceptions import RedisError, ConnectionError as RedisConnectionError
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None
    RedisError = Exception
    RedisConnectionError = Exception

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Redis cache manager with graceful fallback when Redis is unavailable.

    Features:
    - Automatic connection management
    - Graceful degradation if Redis is not available
    - JSON serialization for complex objects
    - TTL support
    - Error handling with fallback to no-cache mode
    """

    def __init__(self, redis_url: Optional[str] = None, default_ttl: int = 3600):
        """
        Initialize cache manager.

        Args:
            redis_url: Redis connection URL (defaults to env REDIS_URL)
            default_ttl: Default time-to-live in seconds (default: 1 hour)
        """
        self.redis_url = redis_url or os.getenv("REDIS_URL")
        self.default_ttl = default_ttl
        self._client: Optional[redis.Redis] = None
        self._enabled = False

        if REDIS_AVAILABLE and self.redis_url:
            try:
                self._client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                # Test connection
                self._client.ping()
                self._enabled = True
                logger.info("Redis cache initialized successfully")
            except (RedisConnectionError, RedisError) as e:
                logger.warning(f"Redis connection failed, caching disabled: {e}")
                self._client = None
                self._enabled = False
        else:
            if not REDIS_AVAILABLE:
                logger.warning("Redis library not installed, caching disabled")
            else:
                logger.warning("REDIS_URL not configured, caching disabled")

    @property
    def is_enabled(self) -> bool:
        """Check if caching is enabled and Redis is available"""
        return self._enabled and self._client is not None

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or cache disabled
        """
        if not self.is_enabled:
            return None

        try:
            value = self._client.get(key)
            if value is None:
                return None

            # Try to deserialize JSON, fall back to raw value
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except (RedisConnectionError, RedisError) as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized if not a string)
            ttl: Time-to-live in seconds (uses default_ttl if not specified)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled:
            return False

        try:
            # Serialize complex objects to JSON
            if not isinstance(value, str):
                value = json.dumps(value)

            ttl = ttl or self.default_ttl
            self._client.setex(key, ttl, value)
            return True
        except (RedisConnectionError, RedisError, TypeError, json.JSONEncodeError) as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled:
            return False

        try:
            self._client.delete(key)
            return True
        except (RedisConnectionError, RedisError) as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        if not self.is_enabled:
            return False

        try:
            return bool(self._client.exists(key))
        except (RedisConnectionError, RedisError) as e:
            logger.error(f"Cache exists error for key '{key}': {e}")
            return False

    def clear(self, pattern: str = "*") -> bool:
        """
        Clear cache keys matching pattern.

        Args:
            pattern: Key pattern to match (default: all keys)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled:
            return False

        try:
            keys = self._client.keys(pattern)
            if keys:
                self._client.delete(*keys)
            return True
        except (RedisConnectionError, RedisError) as e:
            logger.error(f"Cache clear error for pattern '{pattern}': {e}")
            return False


# Global cache instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get or create global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def cache_result(
    key_prefix: str,
    ttl: Optional[int] = None,
    key_builder: Optional[Callable] = None
):
    """
    Decorator to cache function results.

    Args:
        key_prefix: Prefix for cache key
        ttl: Time-to-live in seconds (uses cache default if not specified)
        key_builder: Optional function to build cache key from function args
                    Signature: key_builder(*args, **kwargs) -> str
                    If not provided, uses repr of args/kwargs

    Example:
        @cache_result("agent", ttl=300)
        async def get_agent(db: Session, agent_id: str):
            return db.query(Agent).filter(Agent.id == agent_id).first()

        # With custom key builder
        @cache_result("task", key_builder=lambda db, task_id: f"task:{task_id}")
        async def get_task(db: Session, task_id: str):
            return db.query(Task).filter(Task.id == task_id).first()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache = get_cache_manager()

            # Build cache key
            if key_builder:
                key_suffix = key_builder(*args, **kwargs)
            else:
                # Default key from args/kwargs
                key_parts = [repr(arg) for arg in args]
                key_parts.extend(f"{k}={repr(v)}" for k, v in kwargs.items())
                key_suffix = ":".join(key_parts)

            cache_key = f"{key_prefix}:{key_suffix}"

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            cache.set(cache_key, result, ttl=ttl)
            logger.debug(f"Cache miss, stored result for key: {cache_key}")

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache = get_cache_manager()

            # Build cache key
            if key_builder:
                key_suffix = key_builder(*args, **kwargs)
            else:
                # Default key from args/kwargs
                key_parts = [repr(arg) for arg in args]
                key_parts.extend(f"{k}={repr(v)}" for k, v in kwargs.items())
                key_suffix = ":".join(key_parts)

            cache_key = f"{key_prefix}:{key_suffix}"

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_value

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            cache.set(cache_key, result, ttl=ttl)
            logger.debug(f"Cache miss, stored result for key: {cache_key}")

            return result

        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
