#!/usr/bin/env python3
"""
Debug Models - Check real model IDs from APIs
"""

import sys
import os
from dotenv import load_dotenv

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def debug_gemini():
    """Debug Gemini models"""
    try:
        from google import genai
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("ERROR: GOOGLE_API_KEY not found in .env")
            return
        
        client = genai.Client(api_key=api_key)
        print("--- GEMINI MODELS ---")
        
        for model in client.models.list():
            print(f"ID: {model.name}")
            print(f"Display Name: {model.display_name}")
            print(f"Description: {model.description}")
            print(f"Supported Methods: {getattr(model, 'supported_methods', 'Unknown')}")
            print("---")
            
    except Exception as e:
        print(f"Gemini debug error: {e}")

def debug_groq():
    """Debug Groq models"""
    try:
        import groq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("ERROR: GROQ_API_KEY not found in .env")
            return
        
        client = groq.Groq(api_key=api_key)
        print("--- GROQ MODELS ---")
        
        models = client.models.list()
        for model in models.data:
            print(f"ID: {model.id}")
            print(f"Object: {model.object}")
            print(f"Owned By: {model.owned_by}")
            print(f"Created: {model.created}")
            print(f"Updated: {model.updated}")
            print(f"Context Window: {model.context_window}")
            print("---")
            
    except Exception as e:
        print(f"Groq debug error: {e}")

def main():
    print("=" * 60)
    print("DEBUGGING AI MODEL IDs")
    print("=" * 60)
    
    debug_gemini()
    debug_groq()
    
    print("=" * 60)
    print("DEBUG COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
