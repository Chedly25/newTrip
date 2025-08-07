import redis
import json
import functools
from typing import Any, Callable
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Redis client with error handling
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    # Test connection
    redis_client.ping()
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Caching disabled.")
    redis_client = None

def cache_key_wrapper(key_prefix: str, timeout: int = 3600):
    """Decorator for caching function results"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Skip caching if Redis is not available
            if redis_client is None:
                return await func(*args, **kwargs)
            
            # Create cache key
            cache_key = f"{key_prefix}:{hash(str(args) + str(kwargs))}"
            
            try:
                # Try to get from cache
                cached_result = redis_client.get(cache_key)
                if cached_result:
                    logger.info(f"Cache hit for {cache_key}")
                    return json.loads(cached_result)
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                redis_client.setex(cache_key, timeout, json.dumps(result, default=str))
                logger.info(f"Cached result for {cache_key}")
                
                return result
                
            except Exception as e:
                logger.error(f"Cache error for {cache_key}: {e}")
                # Fall back to executing function without cache
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator