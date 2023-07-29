import aioredis


async def get_redis_pool():
    redis_pool = await aioredis.Redis(host="localhost", port=6379, db=0)
    try:
        yield redis_pool
    finally:
        await redis_pool.close()
