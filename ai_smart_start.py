#!/usr/bin/env python3
"""
SMART AI START - Auto Port Selection - Clean Google GenAI
"""

import sys
import os
import socket
import time
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# FastAPI and AI imports
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import anthropic
import mistralai
import groq
from google import genai

app = FastAPI(title="Aether Multi-Agent Bot - AI", version="1.0.0")

# Request models
class ChatRequest(BaseModel):
    message: str
    model: str = "groq"
    user_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    model: str
    processing_time: float
    tokens_used: int

# AI Model classes
class MistralAI:
    def __init__(self, api_key: str):
        self.client = mistralai.Mistral(api_key=api_key)
    
    async def chat(self, message: str) -> Dict[str, Any]:
        try:
            start_time = time.time()
            response = self.client.chat.complete(
                model="mistral-large-latest",
                messages=[{"role": "user", "content": message}]
            )
            processing_time = time.time() - start_time
            
            return {
                "response": response.choices[0].message.content,
                "processing_time": processing_time,
                "tokens_used": response.usage.total_tokens
            }
        except Exception as e:
            return {"error": str(e), "processing_time": 0, "tokens_used": 0}

class GroqAI:
    def __init__(self, api_key: str):
        self.client = groq.Groq(api_key=api_key)
    
    async def chat(self, message: str) -> Dict[str, Any]:
        try:
            start_time = time.time()
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[{"role": "user", "content": message}],
                max_tokens=1000
            )
            processing_time = time.time() - start_time
            
            return {
                "response": response.choices[0].message.content,
                "processing_time": processing_time,
                "tokens_used": response.usage.total_tokens
            }
        except Exception as e:
            return {"error": str(e), "processing_time": 0, "tokens_used": 0}

class GeminiAI:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-1.5-flash-8b"
    
    async def chat(self, message: str) -> Dict[str, Any]:
        try:
            start_time = time.time()
            response = self.client.models.generate_content(
                model=self.model,
                contents=message
            )
            processing_time = time.time() - start_time
            
            return {
                "response": response.text,
                "processing_time": processing_time,
                "tokens_used": len(response.text.split())
            }
        except Exception as e:
            return {"error": str(e), "processing_time": 0, "tokens_used": 0}

# Initialize AI models
ai_models = {}

def init_ai_models():
    """Initialize AI models with API keys from environment"""
    global ai_models
    
    if os.getenv("MISTRAL_API_KEY"):
        ai_models["mistral"] = MistralAI(os.getenv("MISTRAL_API_KEY"))
    
    if os.getenv("GROQ_API_KEY"):
        ai_models["groq"] = GroqAI(os.getenv("GROQ_API_KEY"))
    
    if os.getenv("GOOGLE_API_KEY"):
        ai_models["gemini"] = GeminiAI(os.getenv("GOOGLE_API_KEY"))

# AI Endpoints
@app.post("/ai/chat")
async def ai_chat(request: ChatRequest):
    """Chat with AI models"""
    if request.model not in ai_models:
        raise HTTPException(status_code=400, detail=f"Model {request.model} not available")
    
    try:
        result = await ai_models[request.model].chat(request.message)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return ChatResponse(
            response=result["response"],
            model=request.model,
            processing_time=result["processing_time"],
            tokens_used=result["tokens_used"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/models")
async def list_models():
    """List available AI models"""
    return {
        "available_models": list(ai_models.keys()),
        "total_models": len(ai_models),
        "models_info": {
            "mistral": "Mistral Large Latest",
            "groq": "Groq Llama 3.1 70B",
            "gemini": "Google Gemini 1.5 Pro"
        }
    }

@app.get("/ai/status")
async def ai_status():
    """Check AI models status"""
    status = {}
    for model_name, model_instance in ai_models.items():
        status[model_name] = {
            "name": model_name,
            "available": True,
            "initialized": True
        }
    
    return {
        "ai_service": "operational",
        "models": status,
        "total_models": len(ai_models)
    }

@app.get("/ai/test/{model}")
async def test_model(model: str):
    """Test specific AI model"""
    if model not in ai_models:
        raise HTTPException(status_code=404, detail=f"Model {model} not found")
    
    try:
        test_message = "Hello! This is a test message."
        result = await ai_models[model].chat(test_message)
        
        return {
            "model": model,
            "test_result": "success",
            "response_preview": result.get("response", "")[:100] + "...",
            "processing_time": result.get("processing_time", 0),
            "tokens_used": result.get("tokens_used", 0)
        }
    except Exception as e:
        return {
            "model": model,
            "test_result": "failed",
            "error": str(e)
        }

def is_port_available(port):
    """Check if port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return True
    except:
        return False

def find_available_port(start_port=8000):
    """Find available port using socket check"""
    port = start_port
    while port < start_port + 100:  # Try up to 100 ports
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('0.0.0.0', port)) != 0:
                return port  # Port is free!
            port += 1  # Port is busy, try next
    return None

if __name__ == "__main__":
    print("Initializing AI models...")
    init_ai_models()
    print(f"Initialized {len(ai_models)} AI models: {list(ai_models.keys())}")
    
    # Find available port FIRST
    print("Finding available port...")
    port = find_available_port()
    
    if not port:
        print("ERROR: No available ports found!")
        sys.exit(1)
    
    print("=" * 60)
    print("AETHER MULTI-AGENT BOT - AI ENDPOINTS")
    print("=" * 60)
    print(f"AI Chat: http://127.0.0.1:{port}/ai/chat")
    print(f"AI Models: http://127.0.0.1:{port}/ai/models")
    print(f"AI Status: http://127.0.0.1:{port}/ai/status")
    print(f"AI Test: http://127.0.0.1:{port}/ai/test/{{model}}")
    print("=" * 60)
    print(f"SUCCESS: Clean Google GenAI - Running on port {port}!")
    print("=" * 60)
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
