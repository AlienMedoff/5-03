#!/usr/bin/env python3
"""
Run Aether Multi-Agent Bot - Windows Compatible
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

# Import and run bot
if __name__ == "__main__":
    try:
        print("Starting Aether Multi-Agent Bot...")
        print(f"Python path: {sys.path[0]}")
        print(f"Current directory: {current_dir}")
        
        # Check if .env exists
        env_file = current_dir / ".env"
        if env_file.exists():
            print("OK: .env file found")
        else:
            print("ERROR: .env file not found!")
            sys.exit(1)
        
        # Import bot
        from bot.main import app
        import uvicorn
        
        print("OK: Bot imported successfully")
        print("Starting server on http://localhost:8080")
        print("Health check: http://localhost:8080/health")
        print("Docs: http://localhost:8080/docs")
        
        uvicorn.run(app, host="0.0.0.0", port=8080)
        
    except ImportError as e:
        print(f"ERROR: Import error: {e}")
        print("Make sure all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
