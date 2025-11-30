import redis

def is_user_online(user_id: int) -> bool:
    r = redis.Redis(host='redis', port=6379, socket_timeout=1)
    is_on = r.exists(f"online:{user_id}")
    r.close()
    return is_on
