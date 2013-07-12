import redis

__author__ = 'Marboni'

cache = None
c = lambda: c

def init_cache(uri):
    global cache
    cache = redis.Redis.from_url(uri)

def recreate_cache(uri):
    redis.Redis.from_url(uri).flushdb()
