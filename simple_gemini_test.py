#!/usr/bin/env python3
"""
Simple Gemini Test - Direct API call
"""

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

def test_gemini_direct():
    """Test Gemini API directly"""
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("ERROR: GOOGLE_API_KEY not found")
            return
        
        client = genai.Client(api_key=api_key)
        print("Testing Gemini API directly...")
        
        # Test with different models
        models_to_test = [
            "gemini-1.5-flash",
            "gemini-2.0-flash-exp",
            "gemini-1.5-flash-8b",
            "gemini-1.5-flash-001"
        ]
        
        for model in models_to_test:
            print(f"\nTesting model: {model}")
            try:
                response = client.models.generate_content(
                    model=model,
                    contents="Hello! This is a test message."
                )
                print(f"SUCCESS: {response.text[:100]}...")
            except Exception as e:
                print(f"ERROR: {e}")
        
    except Exception as e:
        print(f"Setup error: {e}")

if __name__ == "__main__":
    test_gemini_direct()
