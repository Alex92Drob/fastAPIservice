from aiocache import Cache
from aiocache.serializers import PickleSerializer

cache = Cache(Cache.REDIS, serializer=PickleSerializer(), namespace="main", endpoint="localhost", port=6379)


async def set_token(user_id: str, token: str, ttl: int):
    await cache.set(user_id, token, ttl=ttl)

async def get_token(user_id: str):
    return await cache.get(user_id)
