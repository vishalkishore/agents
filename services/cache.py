import redis
import json
import logging
from datetime import datetime
from typing import Optional, Any
from config.settings import settings
from core.logging import log_exception

class CacheService:
    def __init__(self):
        self.logger = logging.getLogger("CacheService")
        self.enabled = settings.CACHE_ENABLED
        if self.enabled:
            self.redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )

    async def get(self, key: str) -> Optional[Any]:
        if not self.enabled:
            return None
            
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            log_exception(self.logger, e, f"Cache get error for key {key}")
            return None

    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        if not self.enabled:
            return False
            
        try:
            ttl = ttl or settings.CACHE_TTL
            value_str = json.dumps(value)
            return self.redis.setex(key, ttl, value_str)
        except Exception as e:
            log_exception(self.logger, e, f"Cache set error for key {key}")
            return False

    def build_key(self, *args) -> str:
        return ":".join(str(arg) for arg in args)
