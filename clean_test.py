#!/usr/bin/env python3
"""
Clean Test - No emojis, just results
"""

import sys
import requests
import json

def test_ai_endpoint(port=8007):
    """Test AI endpoint with all models"""
    base_url = f"http://127.0.0.1:{port}"
    
    print("=" * 60)
    print("AI ROUTER TEST - CHECKING API COMMUNICATION")
    print("=" * 60)
    
    # Test models
    models = ["mistral", "groq", "gemini"]
    test_message = "Hello! This is a test message."
    
    for model in models:
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
    
    # Test models list
    print(f"\nTesting models list...")
    try:
        response = requests.get(f"{base_url}/ai/models", timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            print(f"Models list: {models_data.get('available_models', [])}")
        else:
            print(f"Models list failed: {response.status_code}")
    except Exception as e:
        print(f"Models list error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

def find_server_port():
    """Find which port the server is running on"""
    ports_to_try = [8007, 8008, 8009, 8010]
    
    for port in ports_to_try:
        try:
            response = requests.get(f"http://127.0.0.1:{port}/ai/status", timeout=2)
            if response.status_code == 200:
                print(f"Server found on port {port}")
                return port
        except:
            continue
    
    print("Server not found on ports 8007-8010")
    return None

if __name__ == "__main__":
    print("Looking for AI server...")
    server_port = find_server_port()
    
    if server_port:
        test_ai_endpoint(server_port)
    else:
        print("Please start the AI server first!")
        print("Run: python final_ai_start.py")
