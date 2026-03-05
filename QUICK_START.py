#!/usr/bin/env python3
"""
🚀 Quick Start Script for Aether Multi-Agent Bot
"""

import os
import subprocess
import sys
from pathlib import Path

def check_docker():
    """Check if Docker is available"""
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def check_env_file():
    """Check if .env file exists and is configured"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    with open(env_file, "r") as f:
        content = f.read()
    
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "ALERT_BOT_TOKEN", 
        "ALERT_CHAT_ID",
        "ALLOWED_USERS",
        "ANTHROPIC_API_KEY",
        "MISTRAL_API_KEY",
        "GROQ_API_KEY",
        "GOOGLE_API_KEY",
        "REDIS_PASS",
        "GRAFANA_PASSWORD",
        "SECRET_KEY"
    ]
    
    missing = []
    for var in required_vars:
        if f"{var}=your_" in content or f"{var}=" not in content:
            missing.append(var)
    
    if missing:
        print(f"❌ Missing variables in .env: {missing}")
        return False
    
    return True

def docker_deploy():
    """Deploy with Docker"""
    print("🐳 Deploying with Docker...")
    
    try:
        # Build and start
        subprocess.run(["docker-compose", "up", "-d", "--build"], check=True)
        
        # Wait a moment
        import time
        time.sleep(10)
        
        # Check status
        result = subprocess.run(["docker-compose", "ps"], capture_output=True, text=True)
        
        print("✅ Docker deployment started!")
        print("📊 Container status:")
        print(result.stdout)
        
        print("\n🔗 Services:")
        print("  • Bot API: http://localhost:8080")
        print("  • Health: http://localhost:8080/health")
        print("  • Grafana: http://localhost:3000")
        print("  • Prometheus: http://localhost:9090")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker deployment failed: {e}")
        return False

def local_deploy():
    """Deploy locally"""
    print("🐍 Deploying locally...")
    
    try:
        # Install dependencies
        print("📦 Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        
        # Start bot
        print("🤖 Starting bot...")
        subprocess.run([sys.executable, "bot/main.py"], check=True)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Local deployment failed: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Aether Multi-Agent Bot - Quick Start")
    print("=" * 50)
    
    # Check .env file
    if not check_env_file():
        print("\n❌ Please configure .env file first!")
        return
    
    # Check Docker availability
    if check_docker():
        print("\n✅ Docker found - using Docker deployment")
        docker_deploy()
    else:
        print("\n⚠️ Docker not found - using local deployment")
        local_deploy()

if __name__ == "__main__":
    main()
