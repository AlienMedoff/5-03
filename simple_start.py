#!/usr/bin/env python3
"""
Simple Start for Aether Multi-Agent Bot
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
    return {"message": "Aether Multi-Agent Bot is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "bot": "running"}

@app.get("/docs")
async def docs():
    return {"docs": "FastAPI docs available at /docs"}

if __name__ == "__main__":
    print("Starting Aether Multi-Agent Bot...")
    print("Server: http://localhost:8080")
    print("Health: http://localhost:8080/health")
    print("Docs: http://localhost:8080/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8080)
