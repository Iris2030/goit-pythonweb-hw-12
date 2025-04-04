import redis.asyncio as redis
from conf.config import settings

async def get_redis():
    redis = await redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
    try:
        yield redis
    finally:
        await redis.close()