#!/usr/bin/env python3
"""
Clean Model Discovery - No emojis, pure results
"""

import sys
import requests
import json

def get_available_models_from_server(port=8000):
    """Get available models from server"""
    try:
        response = requests.get(f"http://127.0.0.1:{port}/ai/models", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('available_models', [])
        return []
    except:
        return []

def list_all_possible_models():
    """List all possible models we can try"""
    return [
        "mistral",
        "groq", 
        "gemini",
        "claude",
        "gpt-4",
        "gpt-3.5-turbo"
    ]

def test_model(port, model):
    """Test specific model"""
    try:
        response = requests.post(
            f"http://127.0.0.1:{port}/ai/chat",
            json={
                "message": "Hello! Test message.",
                "model": model,
                "user_id": 123456789
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS {model.upper()}: Working!")
            return True
        else:
            print(f"FAILED {model.upper()}: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR {model.upper()}: {e}")
        return False

def find_server_port():
    """Find server port"""
    for port in range(8000, 8020):
        try:
            response = requests.get(f"http://127.0.0.1:{port}/ai/status", timeout=1)
            if response.status_code == 200:
                print(f"Server found on port {port}")
                return port
        except:
            continue
    return None

if __name__ == "__main__":
    print("=" * 60)
    print("CLEAN MODEL DISCOVERY")
    print("=" * 60)
    
    # Find server
    server_port = find_server_port()
    if not server_port:
        print("ERROR: Server not found!")
        sys.exit(1)
    
    # Get available models from server
    available_models = get_available_models_from_server(server_port)
    print(f"Server reports available models: {available_models}")
    
    # Test all possible models
    all_models = list_all_possible_models()
    print(f"Testing all possible models: {all_models}")
    
    working_models = []
    
    for model in all_models:
        print(f"\nTesting {model}...")
        if test_model(server_port, model):
            working_models.append(model)
    
    print("\n" + "=" * 60)
    print("DISCOVERY RESULTS:")
    print(f"Working models: {working_models}")
    print(f"Total tested: {len(all_models)}")
    print(f"Success rate: {len(working_models)}/{len(all_models)}")
    print("=" * 60)
