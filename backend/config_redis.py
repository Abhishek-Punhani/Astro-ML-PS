import redis

redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
data_redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
