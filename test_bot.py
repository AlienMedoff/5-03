import asyncio
from aiogram import Bot, Dispatcher

async def main():
    # Вставляем НОВЫЙ токен прямо сюда, минуя .env
    token = "8592837465:AAHLgoAIr_jkRJUhPkFJsOT2RBJk2s1o4sM"
    
    print("Запускаем тестового бота...")
    bot = Bot(token=token)
    dp = Dispatcher()
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
