import asyncio
import logging
import aiohttp
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from dotenv import load_dotenv

# Загружаем настройки
load_dotenv()
# Вставляем НОВЫЙ токен прямо сюда, минуя .env
BOT_TOKEN = "8652950916:AAHoJAJRbU58bH6P4ic7gOLRoZwcpp9PJ7k"
AI_SERVER_URL = "http://127.0.0.1:8000/ai/chat"

# Настройка логов
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def get_ai_response(text, user_id):
    """Стучится в твой локальный Aether API"""
    payload = {
        "message": text,
        "model": "mistral", # По умолчанию используем стабильный Mistral
        "user_id": user_id
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(AI_SERVER_URL, json=payload) as resp:
                data = await resp.json()
                return data.get("response", "AI вернул пустой ответ.")
        except Exception as e:
            return f"❌ Сервер Aether недоступен: {str(e)}"

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("🚀 Привет! Я Aether Bot. Бэкенд подключен, ИИ готов. Жду твое сообщение!")

@dp.message()
async def handle_message(message: types.Message):
    # Показываем, что бот печатает
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    # Получаем ответ от твоего сервера
    response = await get_ai_response(message.text, message.from_user.id)
    # Отправляем в Telegram
    await message.answer(response)

async def main():
    print("=" * 60)
    print("AETHER MVP BOT STARTING...")
    print("=" * 60)
    
    # Сброс кэша Telegram (убивает конфликты)
    await bot.delete_webhook(drop_pending_updates=True)
    
    # ЕДИНСТВЕННАЯ ТОЧКА ЗАПУСКА:
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
