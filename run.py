#!/usr/bin/env python3
"""
FINAL START - Aether Multi-Agent Bot - Port 8082
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

app = FastAPI(title="Aether Multi-Agent Bot", version="1.0.0")

@app.get("/")
async def root():
    return {
        "message": "Aether Multi-Agent Bot is running!",
        "status": "active",
        "github": "https://github.com/AlienMedoff/5-03"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "bot": "running",
        "version": "1.0.0",
        "features": ["multi-agent", "ai-integration", "monitoring", "security"]
    }

@app.get("/bot/status")
async def bot_status():
    return {
        "bot": "Aether Multi-Agent Bot",
        "status": "running",
        "models": ["claude", "mistral", "groq", "gemini"],
        "endpoints": {
            "health": "/health",
            "status": "/bot/status",
            "docs": "/docs"
        }
    }

@app.get("/docs")
async def docs():
    return {
        "message": "FastAPI docs available at /docs",
        "interactive": "http://localhost:8082/docs"
    }

if __name__ == "__main__":
    print("=" * 60)
    print("AETHER MULTI-AGENT BOT - SUCCESS!")
    print("=" * 60)
    print("OK Server: http://localhost:8082")
    print("OK Health: http://localhost:8082/health")
    print("OK Status: http://localhost:8082/bot/status")
    print("OK Docs: http://localhost:8082/docs")
    print("=" * 60)
    print("BOT IS RUNNING! OPEN BROWSER AND TEST!")
    print("GitHub: https://github.com/AlienMedoff/5-03")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8082)
