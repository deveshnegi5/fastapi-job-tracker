from fastapi import FastAPI
# from fastapi_cache.decorator import cache
from starlette.requests import Request
from starlette.responses import Response
import os
from contextlib import asynccontextmanager
from redis import asyncio
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.backends.inmemory import InMemoryBackend

@asynccontextmanager
async def lifespan(_:FastAPI):
    if os.getenv("TESTING") == "1":
        FastAPICache.init(InMemoryBackend(), prefix="api-cache")
    else:
        redis = asyncio.from_url(os.getenv("REDIS_URL"))
        FastAPICache.init(RedisBackend(redis), prefix="api-cache")
    yield

def user_key_builder(func,namespace:str="", request:Request=None,response:Response=None,*args,**kwargs):
    user=kwargs.get("user")
    user_id=user.id if user else None
    query= request.query_params if request else ""
    key= f"{namespace}:{func.__module__}:{func.__name__}:{user_id}:{query}"
    # print("CACHE KEY:", key)   # TEMPORARY
    return key
