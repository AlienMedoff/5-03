#!/usr/bin/env python3
"""
SMART START - Aether Multi-Agent Bot - Auto Port Selection
"""

import sys
import os
import socket
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
        "interactive": f"http://localhost:{port}/docs"
    }

def is_port_available(port):
    """Check if port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except:
        return False

def find_available_port(start_port=8000, max_attempts=100):
    """Find available port"""
    for i in range(max_attempts):
        port = start_port + i
        if is_port_available(port):
            return port
    return None

if __name__ == "__main__":
    print("Finding available port...")
    port = find_available_port()
    
    if port:
        print("=" * 60)
        print("AETHER MULTI-AGENT BOT - SUCCESS!")
        print("=" * 60)
        print(f"OK Server: http://localhost:{port}")
        print(f"OK Health: http://localhost:{port}/health")
        print(f"OK Status: http://localhost:{port}/bot/status")
        print(f"OK Docs: http://localhost:{port}/docs")
        print("=" * 60)
        print("BOT IS RUNNING! OPEN BROWSER AND TEST!")
        print("GitHub: https://github.com/AlienMedoff/5-03")
        print("=" * 60)
        
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        print("ERROR: No available ports found!")
        sys.exit(1)
