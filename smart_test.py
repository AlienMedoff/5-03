#!/usr/bin/env python3
"""
Smart Test - Dynamic model detection + UTF-8 fix
"""

import sys
import requests
import json

# Force UTF-8 output for Windows console
sys.stdout.reconfigure(encoding='utf-8')

def get_available_models(port=8007):
    """Get available models from server"""
    try:
        response = requests.get(f"http://127.0.0.1:{port}/ai/models", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('available_models', [])
        return []
    except:
        return []

def test_ai_endpoint(port=8007):
    """Test AI endpoint with dynamically fetched models"""
    base_url = f"http://127.0.0.1:{port}"
    
    print("=" * 60)
    print("AI ROUTER TEST - DYNAMIC MODEL DETECTION")
    print("=" * 60)
    
    # Get available models first
    available_models = get_available_models(port)
    print(f"Available models: {available_models}")
    
    if not available_models:
        print("No models available!")
        return
    
    test_message = "Hello! This is a test message."
    
    # Test each available model
    for model in available_models:
        print(f"\nTesting {model.upper()} model...")
        
        try:
            response = requests.post(
                f"{base_url}/ai/chat",
                json={
                    "message": test_message,
                    "model": model,
                    "user_id": 123456789
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"SUCCESS {model.upper()}:")
                print(f"   Response: {result.get('response', 'No response')[:100]}...")
                print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
                print(f"   Tokens used: {result.get('tokens_used', 0)}")
            else:
                print(f"FAILED {model.upper()}:")
                print(f"   Status: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"TIMEOUT {model.upper()}:")
        except requests.exceptions.ConnectionError:
            print(f"CONNECTION ERROR {model.upper()}:")
        except Exception as e:
            print(f"ERROR {model.upper()}: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

def find_server_port():
    """Find which port is server is running on"""
    ports_to_try = [8005, 8004, 8003, 8002, 8001, 8000, 8006, 8007, 8008, 8009, 8010]
    
    for port in ports_to_try:
        try:
            response = requests.get(f"http://127.0.0.1:{port}/ai/status", timeout=2)
            if response.status_code == 200:
                print(f"Server found on port {port}")
                return port
        except:
            continue
    
    print("Server not found on ports 8000-8010")
    return None

if __name__ == "__main__":
    print("Looking for AI server...")
    server_port = find_server_port()
    
    if server_port:
        test_ai_endpoint(server_port)
    else:
        print("Please start the AI server first!")
        print("Run: python final_ai_start.py")
