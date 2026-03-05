import json
import os
import time
import redis.asyncio as redis

REDIS_URL   = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_PASS  = os.getenv("REDIS_PASS")
MAX_CONTEXT = 50  # последних сообщений в контексте

_client = None

async def get_client():
    global _client
    if _client is None:
        _client = redis.from_url(REDIS_URL, password=REDIS_PASS, decode_responses=True)
    return _client

# ============================================================
# СЕССИЯ — контекст разговора (без TTL, живёт вечно)
# ============================================================

async def add_to_session(user_id: int, role: str, content: str) -> None:
    r   = await get_client()
    key = f"session:{user_id}"
    msg = json.dumps({"role": role, "content": content})
    await r.rpush(key, msg)
    await r.ltrim(key, -MAX_CONTEXT, -1)
    # БЕЗ expire — живёт пока сам не сбросишь

async def get_session(user_id: int) -> list:
    r    = await get_client()
    key  = f"session:{user_id}"
    msgs = await r.lrange(key, 0, -1)
    return [json.loads(m) for m in msgs]

async def archive_session(user_id: int) -> None:
    """При /reset — не удаляем, а перекладываем в архив с меткой времени"""
    r       = await get_client()
    key     = f"session:{user_id}"
    msgs    = await r.lrange(key, 0, -1)
    if not msgs:
        return
    archive_key = f"archive:{user_id}:{int(time.time())}"
    for msg in msgs:
        await r.rpush(archive_key, msg)
    # архив тоже без TTL
    await r.delete(key)

async def get_archives(user_id: int) -> list:
    """Список всех архивных сессий"""
    r    = await get_client()
    keys = await r.keys(f"archive:{user_id}:*")
    keys.sort()
    result = []
    for k in keys:
        msgs = await r.lrange(k, 0, -1)
        ts   = k.split(":")[-1]
        result.append({
            "timestamp": int(ts),
            "messages":  [json.loads(m) for m in msgs]
        })
    return result

async def restore_session(user_id: int, timestamp: int) -> bool:
    """Восстановить архивную сессию"""
    r           = await get_client()
    archive_key = f"archive:{user_id}:{timestamp}"
    msgs        = await r.lrange(archive_key, 0, -1)
    if not msgs:
        return False
    key = f"session:{user_id}"
    await r.delete(key)
    for msg in msgs:
        await r.rpush(key, msg)
    return True

# ============================================================
# ИСТОРИЯ дебатов
# ============================================================

async def save_debate(user_id: int, question: str, consensus: str) -> None:
    r     = await get_client()
    key   = f"history:{user_id}"
    entry = json.dumps({"question": question, "consensus": consensus})
    await r.lpush(key, entry)
    await r.ltrim(key, 0, 99)  # последние 100

async def get_history(user_id: int) -> list:
    r     = await get_client()
    key   = f"history:{user_id}"
    items = await r.lrange(key, 0, 4)
    return [json.loads(i) for i in items]

# ============================================================
# КЭШ
# ============================================================

async def cache_set(key: str, value: str, ttl: int = 300) -> None:
    r = await get_client()
    await r.setex(f"cache:{key}", ttl, value)

async def cache_get(key: str) -> str | None:
    r = await get_client()
    return await r.get(f"cache:{key}")
