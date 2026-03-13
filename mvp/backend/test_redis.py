
import redis
try:
    r = redis.from_url("redis://localhost:6379/0")
    r.ping()
    print("Redis is RUNNING")
except Exception as e:
    print(f"Redis is NOT RUNNING: {e}")
