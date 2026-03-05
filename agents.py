import os
from litellm import completion

AGENTS = {
    "Claude": {
        "model": "claude-3-5-sonnet-20241022",
        "api_key_env": "ANTHROPIC_API_KEY",
        "emoji": "🧠",
    },
    "Gemini": {
        "model": "gemini/gemini-1.5-flash",
        "api_key_env": "GOOGLE_API_KEY",
        "emoji": "⚡",
    },
    "Mistral": {
        "model": "mistral/mistral-large-latest",
        "api_key_env": "MISTRAL_API_KEY",
        "emoji": "🌪",
    },
    "Groq": {
        "model": "groq/llama-3.1-70b-versatile",
        "api_key_env": "GROQ_API_KEY",
        "emoji": "🚀",
    },
}

SYSTEM_PROMPT = """Ты — AI-агент в команде разработчиков.
Ты помнишь весь предыдущий контекст разговора.
Давай чёткий технический ответ, пиши код если нужно.
Не повторяй других агентов. Максимум 300 слов."""

JUDGE_PROMPT = """Ты — судья AI-дебатов. Ты помнишь весь контекст разговора.
Тебе дали ответы нескольких агентов на одну задачу.
1. Выбери лучшие идеи из каждого ответа
2. Объедини в один чёткий консенсус
3. Реши противоречия
4. Дай финальный ответ с кодом если нужно
Максимум 500 слов."""

def ask_agent(name: str, question: str, context: list = None) -> str:
    cfg      = AGENTS[name]
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if context:
        messages.extend(context)
    messages.append({"role": "user", "content": question})
    try:
        resp = completion(
            model=cfg["model"],
            messages=messages,
            max_tokens=800,
            api_key=os.getenv(cfg["api_key_env"]),
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"[Ошибка: {e}]"

def make_consensus(question: str, answers: dict, context: list = None) -> str:
    combined = f"Вопрос: {question}\n\n"
    for name, answer in answers.items():
        combined += f"--- {name} ---\n{answer}\n\n"
    messages = [{"role": "system", "content": JUDGE_PROMPT}]
    if context:
        messages.extend(context)
    messages.append({"role": "user", "content": combined})
    try:
        resp = completion(
            model="claude-3-5-sonnet-20241022",
            messages=messages,
            max_tokens=1200,
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"[Ошибка консенсуса: {e}]"
