from redis import Redis
import os

# Read from env vars or fallback to localhost
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Single shared Redis connection
redis_conn = Redis.from_url(REDIS_URL)
