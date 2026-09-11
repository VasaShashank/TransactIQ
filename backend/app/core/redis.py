import redis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class RedisManager:
    _client: redis.Redis | None = None
    _unavailable: bool = False

    @classmethod
    def get_client(cls) -> redis.Redis | None:
        if cls._unavailable:
            return None
        if cls._client is None:
            try:
                cls._client = redis.Redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_timeout=2,
                    socket_connect_timeout=2
                )
                cls._client.ping()
            except Exception as e:
                logger.warning(f"Redis is not available, caching will be disabled: {e}")
                cls._client = None
                cls._unavailable = True
                return None
        return cls._client

def get_redis():
    client = RedisManager.get_client()
    return client
