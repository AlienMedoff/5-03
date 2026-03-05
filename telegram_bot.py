#!/usr/bin/env python3
"""
Telegram Bot for Aether Multi-Agent System
"""

import sys
import os
import asyncio
import requests
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Telegram imports
try:
    from aiogram import Bot, Dispatcher, types, F
except ImportError:
    print("ERROR: aiogram not installed. Install with: pip install aiogram")
    sys.exit(1)

# Bot configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AI_SERVER_URL = "http://127.0.0.1:8000"  # Update if your AI server runs on different port

if not BOT_TOKEN:
    print("ERROR: TELEGRAM_BOT_TOKEN not found in .env file")
    sys.exit(1)

# Initialize bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# AI Server communication
async def call_ai_server(message: str, model: str = "mistral") -> dict:
    """Call AI server and get response"""
    try:
        response = requests.post(
            f"{AI_SERVER_URL}/ai/chat",
            json={
                "message": message,
                "model": model,
                "user_id": 0  # Will be replaced with actual user_id
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"AI Server error: {response.status_code}"}
            
    except Exception as e:
        return {"error": f"Connection error: {str(e)}"}

# Bot handlers
@dp.message()
async def send_welcome(message: types.Message):
    """Send welcome message"""
    await message.answer(
        "🤖 *Aether Multi-Agent Bot* activated!\n\n"
        "Available commands:\n"
        "/chat - Chat with AI\n"
        "/models - List available AI models\n"
        "/help - Show this help"
    )

@dp.message(commands=["chat"])
async def handle_chat(message: types.Message):
    """Handle chat command"""
    # Extract message after command
    if len(message.text.split()) > 1:
        user_message = " ".join(message.text.split()[1:])
    else:
        await message.answer("Please provide a message after /chat command")
        return
    
    await message.answer("🤔 Thinking...")
    
    # Call AI server
    result = await call_ai_server(user_message)
    
    if "error" in result:
        await message.answer(f"❌ Error: {result['error']}")
    else:
        response_text = result.get("response", "No response")
        processing_time = result.get("processing_time", 0)
        tokens_used = result.get("tokens_used", 0)
        
        await message.answer(
            f"🤖 *{result.get('model', 'AI').upper()}* Response:\n\n"
            f"{response_text[:500]}...\n\n"
            f"⏱️ Time: {processing_time:.2f}s\n"
            f"🔢 Tokens: {tokens_used}"
        )

@dp.message(commands=["models"])
async def handle_models(message: types.Message):
    """Handle models command"""
    try:
        response = requests.get(f"{AI_SERVER_URL}/ai/models", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            models_list = data.get("available_models", [])
            models_info = data.get("models_info", {})
            
            text = "🤖 *Available AI Models:*\n\n"
            for model in models_list:
                info = models_info.get(model, {})
                text += f"• *{model.upper()}*: {info}\n"
            
            await message.answer(text)
        else:
            await message.answer("❌ Failed to get models list")
            
    except Exception as e:
        await message.answer(f"❌ Error: {str(e)}")

@dp.message(commands=["help"])
async def handle_help(message: types.Message):
    """Handle help command"""
    await message.answer(
        "🤖 *Aether Multi-Agent Bot Help*\n\n"
        "Commands:\n"
        "/chat <message> - Chat with AI\n"
        "/models - List available AI models\n"
        "/help - Show this help\n\n"
        "Example: /chat Hello, how are you?"
    )

@dp.message()
async def handle_text(message: types.Message):
    """Handle regular text messages"""
    # Default to chat if no command
    await handle_chat(message)

async def main():
    """Start bot"""
    print("=" * 60)
    print("AETHER TELEGRAM BOT")
    print("=" * 60)
    print(f"AI Server URL: {AI_SERVER_URL}")
    print(f"Bot Token: {BOT_TOKEN[:20]}...")
    print("=" * 60)
    
    # Start bot
    try:
        await dp.start_polling()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Bot error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
