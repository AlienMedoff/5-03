import asyncio
import hashlib
import json
import logging
import os
import time
from collections import defaultdict
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiohttp import web
from debate import run_debate
from agents import AGENTS
from memory import (
    save_debate, get_history,
    add_to_session, get_session,
    archive_session, get_archives, restore_session
)

load_dotenv()
logging.basicConfig(level=logging.INFO)

# ============================================================
# КОНФИГ
# ============================================================

ALLOWED_USERS = set(
    int(x) for x in os.getenv("ALLOWED_USERS", "").split(",") if x.strip()
)
RATE_LIMIT     = int(os.getenv("RATE_LIMIT", "10"))
AUDIT_LOG_PATH = os.getenv("AUDIT_LOG", "audit.log")

bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp  = Dispatcher()

_start_time   = time.time()
_debate_count = 0
_error_count  = 0

# ============================================================
# AUDIT
# ============================================================

def audit_log(user_id: int, action: str, payload: dict) -> None:
    entry = {
        "user_id":   user_id,
        "action":    action,
        "payload":   payload,
        "timestamp": time.time(),
    }
    entry_str  = json.dumps(entry, sort_keys=True, ensure_ascii=False)
    entry_hash = hashlib.sha256(entry_str.encode()).hexdigest()
    with open(AUDIT_LOG_PATH, "a") as f:
        f.write(f"{entry_hash} {entry_str}\n")
    logging.info(f"[audit] {action} user={user_id} -> {entry_hash[:12]}")

# ============================================================
# RATE LIMIT
# ============================================================

_rate_buckets: dict = defaultdict(list)

def check_rate_limit(user_id: int) -> bool:
    now = time.time()
    _rate_buckets[user_id] = [t for t in _rate_buckets[user_id] if now - t < 60]
    if len(_rate_buckets[user_id]) >= RATE_LIMIT:
        return False
    _rate_buckets[user_id].append(now)
    return True

# ============================================================
# SECURITY FILTER
# ============================================================

FORBIDDEN = ["rm -rf", "DROP TABLE", "os.system", "eval(", "<script>"]

def security_check(text: str) -> tuple[bool, str]:
    for pattern in FORBIDDEN:
        if pattern.lower() in text.lower():
            return False, f"Запрещённый паттерн: {pattern!r}"
    if len(text) > 4000:
        return False, "Сообщение слишком длинное (макс 4000 символов)"
    return True, ""

# ============================================================
# GUARD
# ============================================================

async def guard(message: types.Message) -> bool:
    uid = message.from_user.id
    if ALLOWED_USERS and uid not in ALLOWED_USERS:
        audit_log(uid, "ACCESS_DENIED", {"text": message.text[:50]})
        await message.answer("⛔ Доступ запрещён")
        return False
    if not check_rate_limit(uid):
        audit_log(uid, "RATE_LIMITED", {})
        await message.answer(f"⏳ Слишком много запросов. Макс {RATE_LIMIT}/мин")
        return False
    ok, reason = security_check(message.text or "")
    if not ok:
        audit_log(uid, "SECURITY_BLOCKED", {"reason": reason})
        await message.answer(f"🚫 Заблокировано: {reason}")
        return False
    return True

# ============================================================
# HANDLERS
# ============================================================

@dp.message(CommandStart())
async def start(message: types.Message):
    uid   = message.from_user.id
    names = " · ".join(f"{cfg['emoji']}{name}" for name, cfg in AGENTS.items())
    audit_log(uid, "START", {})
    await message.answer(
        f"👋 *Aether Multi-Agent Hub*\n\n"
        f"Агенты: {names}\n\n"
        f"Пиши задачу — все агенты обсудят и дадут консенсус.\n\n"
        f"/agents — список агентов\n"
        f"/history — последние дебаты\n"
        f"/archives — архивные сессии\n"
        f"/reset — архивировать и начать заново\n"
        f"/status — статус системы",
        parse_mode="Markdown"
    )

@dp.message(Command("agents"))
async def agents_cmd(message: types.Message):
    if not await guard(message):
        return
    text = "🤖 *Активные агенты:*\n\n"
    for name, cfg in AGENTS.items():
        text += f"{cfg['emoji']} *{name}* — `{cfg['model']}`\n"
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("history"))
async def history_cmd(message: types.Message):
    if not await guard(message):
        return
    uid     = message.from_user.id
    history = await get_history(uid)
    if not history:
        await message.answer("📭 История пуста")
        return
    text = "📚 *Последние дебаты:*\n\n"
    for i, item in enumerate(history, 1):
        q     = item["question"][:80]
        short = item["consensus"][:150]
        text += f"*{i}.* {q}...\n_{short}..._\n\n"
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("reset"))
async def reset_cmd(message: types.Message):
    if not await guard(message):
        return
    uid = message.from_user.id
    await archive_session(uid)
    audit_log(uid, "SESSION_ARCHIVED", {})
    await message.answer(
        "📦 Сессия заархивирована.\n"
        "Начинаем с чистого листа.\n"
        "Вернуться к старой сессии: /archives"
    )

@dp.message(Command("archives"))
async def archives_cmd(message: types.Message):
    if not await guard(message):
        return
    uid      = message.from_user.id
    archives = await get_archives(uid)
    if not archives:
        await message.answer("📭 Архив пуст")
        return
    text = "🗄 *Архивные сессии:*\n\n"
    for a in archives[-5:]:
        ts      = a["timestamp"]
        count   = len(a["messages"])
        dt      = time.strftime("%d.%m.%Y %H:%M", time.localtime(ts))
        text   += f"📁 `{ts}` — {dt} ({count} сообщений)\n"
        text   += f"Восстановить: `/restore {ts}`\n\n"
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("restore"))
async def restore_cmd(message: types.Message):
    if not await guard(message):
        return
    uid  = message.from_user.id
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Использование: /restore <timestamp>")
        return
    try:
        ts = int(args[1])
    except ValueError:
        await message.answer("❌ Неверный timestamp")
        return
    ok = await restore_session(uid, ts)
    if ok:
        audit_log(uid, "SESSION_RESTORED", {"timestamp": ts})
        await message.answer("✅ Сессия восстановлена. Продолжаем с того места.")
    else:
        await message.answer("❌ Архив не найден")

@dp.message(Command("status"))
async def status_cmd(message: types.Message):
    if not await guard(message):
        return
    uid     = message.from_user.id
    now     = time.time()
    recent  = len([t for t in _rate_buckets[uid] if now - t < 60])
    uptime  = int(now - _start_time)
    h, m    = divmod(uptime // 60, 60)
    context = await get_session(uid)
    await message.answer(
        f"📊 *Статус системы*\n\n"
        f"⏱ Аптайм: {h}ч {m}м\n"
        f"💬 Дебатов: {_debate_count}\n"
        f"❌ Ошибок: {_error_count}\n"
        f"📨 Запросов за минуту: {recent}/{RATE_LIMIT}\n"
        f"🤖 Агентов: {len(AGENTS)}\n"
        f"🧠 Сообщений в контексте: {len(context)}",
        parse_mode="Markdown"
    )

@dp.message()
async def handle(message: types.Message):
    global _debate_count, _error_count
    if not await guard(message):
        return

    uid      = message.from_user.id
    question = message.text or ""
    context  = await get_session(uid)

    audit_log(uid, "DEBATE_START", {"question": question[:200]})
    status = await message.answer("🔄 Запускаю дебаты...")

    async def on_agent_done(name, answer):
        cfg   = AGENTS[name]
        short = answer[:300] + "..." if len(answer) > 300 else answer
        await message.answer(
            f"{cfg['emoji']} *{name}*:\n\n{short}",
            parse_mode="Markdown"
        )

    try:
        result = await run_debate(
            question,
            context=context,
            progress_callback=on_agent_done
        )
        _debate_count += 1
        await add_to_session(uid, "user", question)
        await add_to_session(uid, "assistant", result["consensus"])
        await save_debate(uid, question, result["consensus"])
        audit_log(uid, "DEBATE_DONE", {"consensus_len": len(result["consensus"])})
        await status.edit_text("✅ Дебаты завершены")
        await message.answer(
            f"🎯 *КОНСЕНСУС*\n\n{result['consensus']}",
            parse_mode="Markdown"
        )
    except Exception as e:
        _error_count += 1
        audit_log(uid, "DEBATE_ERROR", {"error": str(e)})
        await status.edit_text(f"❌ Ошибка: {e}")

# ============================================================
# HEALTH + METRICS
# ============================================================

async def healthcheck(request):
    return web.json_response({
        "status":  "ok",
        "uptime":  round(time.time() - _start_time),
        "debates": _debate_count,
        "errors":  _error_count,
        "agents":  list(AGENTS.keys()),
    })

async def metrics(request):
    return web.Response(
        content_type="text/plain",
        text=(
            "# HELP aether_uptime_seconds Bot uptime\n"
            "# TYPE aether_uptime_seconds counter\n"
            f"aether_uptime_seconds {round(time.time() - _start_time)}\n"
            "# HELP aether_debates_total Debates processed\n"
            "# TYPE aether_debates_total counter\n"
            f"aether_debates_total {_debate_count}\n"
            "# HELP aether_errors_total Errors occurred\n"
            "# TYPE aether_errors_total counter\n"
            f"aether_errors_total {_error_count}\n"
            "# HELP aether_agents_total Agents configured\n"
            "# TYPE aether_agents_total gauge\n"
            f"aether_agents_total {len(AGENTS)}\n"
        )
    )

async def start_health_server():
    app = web.Application()
    app.router.add_get("/health", healthcheck)
    app.router.add_get("/metrics", metrics)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    logging.info("Health/metrics server started on :8080")

# ============================================================
# MAIN
# ============================================================

async def main():
    logging.info("Aether Bot starting...")
    await asyncio.gather(
        dp.start_polling(bot),
        start_health_server(),
    )

if __name__ == "__main__":
    asyncio.run(main())
