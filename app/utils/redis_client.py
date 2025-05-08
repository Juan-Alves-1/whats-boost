import redis
from app.config.settings import settings

# Redis client instance (decode_responses=True ensures string output)
redis_url = settings.REDIS_URL
redis_client = redis.Redis.from_url(redis_url, decode_responses=True)

def acquire_user_lock(email: str, ttl: int = 600) -> bool:
    """
    Attempts to acquire a lock for a user. Returns True if acquired.
    """
    key = f"lock:user:{email}"
    return redis_client.set(name=key, value="1", ex=ttl, nx=True)  # NX means only set if not exists


def release_user_lock(email: str):
    """
    Releases the lock for a user.
    """
    key = f"lock:user:{email}"
    redis_client.delete(key)


def get_user_lock_status(email: str) -> bool:
    """
    Returns True if the user lock is active.
    """
    key = f"lock:user:{email}"
    return redis_client.exists(key) == 1