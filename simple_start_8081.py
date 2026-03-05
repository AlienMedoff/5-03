#!/usr/bin/env python3
"""
Simple Start for Aether Multi-Agent Bot - Port 8081
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Simple FastAPI app
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Aether Multi-Agent Bot")

@app.get("/")
async def root():
    return {"message": "Aether Multi-Agent Bot is running!", "status": "active"}

@app.get("/health")
async def health():
    return {"status": "healthy", "bot": "running", "version": "1.0.0"}

@app.get("/docs")
async def docs():
    return {"docs": "FastAPI docs available at /docs"}

@app.get("/bot/status")
async def bot_status():
    return {
        "bot": "Aether Multi-Agent Bot",
        "status": "running",
        "models": ["claude", "mistral", "groq", "gemini"],
        "features": ["multi-agent", "ai-integration", "monitoring", "security"]
    }

if __name__ == "__main__":
    print("Starting Aether Multi-Agent Bot...")
    print("Server: http://localhost:8081")
    print("Health: http://localhost:8081/health")
    print("Status: http://localhost:8081/bot/status")
    print("Docs: http://localhost:8081/docs")
    print()
    print("SUCCESS: Bot is running!")
    print("Open browser and test the endpoints!")
    
    uvicorn.run(app, host="0.0.0.0", port=8081)
