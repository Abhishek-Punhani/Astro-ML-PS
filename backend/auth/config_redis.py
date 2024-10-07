import os
import redis


redis_client_name=os.getenv("REDIS_CLIENT_HOST_NAME")
redis_client_pass=os.getenv("REDIS_CLIENT_HOST_PASS")
data_redis_client_name=os.getenv("REDIS_DATA_CLIENT_HOST_NAME")
data_redis_client_pass=os.getenv("REDIS_DATA_CLIENT_HOST_PASS")


redis_client = redis.StrictRedis(host=redis_client_name,
  port=6379,
  password=redis_client_pass,
  ssl=True)
data_redis_client = redis.StrictRedis(host=data_redis_client_name,
  port=6379,
  password=data_redis_client_pass,
  ssl=True)