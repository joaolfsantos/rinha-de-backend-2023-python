from redis.asyncio import from_url
from app.config.env import REDIS_URI


redis_cache = from_url(REDIS_URI, decode_responses=True)
