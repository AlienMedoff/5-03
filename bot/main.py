"""
🤖 Main Telegram Bot Module
Aether Multi-Agent Bot - Enterprise Telegram Interface
"""

import asyncio
import logging
from typing import Dict, Any
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest

from core.config import settings
from core.security import security_manager, SecurityLevel
from bot.handlers import router as bot_router
from agents.hub import agent_hub


# 📊 Prometheus Metrics
REQUEST_COUNT = Counter('bot_requests_total', 'Total bot requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('bot_response_time_seconds', 'Bot response time')
ERROR_COUNT = Counter('bot_errors_total', 'Total bot errors', ['error_type'])


# 🚀 Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """🚀 Application startup and shutdown"""
    
    # Startup
    logging.info("🚀 Starting Aether Multi-Agent Bot...")
    
    # Initialize security manager
    security_manager.cleanup_old_data()
    
    # Initialize AI agent hub
    await agent_hub.initialize()
    
    logging.info("✅ Bot started successfully")
    
    yield
    
    # Shutdown
    logging.info("🛑 Shutting down Aether Multi-Agent Bot...")
    
    # Cleanup
    await agent_hub.cleanup()
    
    logging.info("✅ Bot shutdown complete")


# 🤖 FastAPI Application
app = FastAPI(
    title="Aether Multi-Agent Bot",
    description="Enterprise multi-agent Telegram bot with AI integration",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)


# 🔧 Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# 📊 Metrics endpoint
@app.get("/metrics")
async def metrics():
    """📊 Prometheus metrics endpoint"""
    return generate_latest()


# 🏥 Health check endpoint
@app.get("/health")
async def health_check():
    """🏥 Health check endpoint"""
    try:
        # Check Redis connection
        redis_status = await agent_hub.health_check()
        
        # Check security status
        security_stats = security_manager.get_security_stats()
        
        health_status = {
            "status": "healthy",
            "timestamp": asyncio.get_event_loop().time(),
            "version": "1.0.0",
            "services": {
                "redis": redis_status,
                "security": security_stats["security_level"],
                "ai_hub": await agent_hub.get_status()
            },
            "metrics": {
                "total_requests": REQUEST_COUNT._value.get(),
                "error_rate": ERROR_COUNT._value.get() / max(REQUEST_COUNT._value.get(), 1)
            }
        }
        
        return health_status
        
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


# 🤖 Bot status endpoint
@app.get("/status")
async def bot_status():
    """📊 Detailed bot status"""
    try:
        return {
            "bot": {
                "status": "running",
                "allowed_users": len(settings.allowed_users),
                "active_sessions": await agent_hub.get_active_sessions_count(),
                "default_model": settings.default_model,
                "features": {
                    "monitoring": settings.enable_monitoring,
                    "alerts": settings.enable_alerts,
                    "audit": settings.enable_audit,
                    "cache": settings.enable_cache,
                    "sessions": settings.enable_sessions
                }
            },
            "ai_models": {
                "claude": bool(settings.anthropic_api_key),
                "mistral": bool(settings.mistral_api_key),
                "groq": bool(settings.groq_api_key),
                "gemini": bool(settings.google_api_key)
            },
            "security": security_manager.get_security_stats(),
            "performance": {
                "worker_processes": settings.worker_processes,
                "max_connections": settings.max_connections,
                "rate_limit": settings.rate_limit
            }
        }
        
    except Exception as e:
        logging.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")


# 📊 Analytics endpoint
@app.get("/analytics")
async def analytics():
    """📊 Bot analytics and statistics"""
    try:
        return {
            "usage": {
                "total_requests": REQUEST_COUNT._value.get(),
                "total_errors": ERROR_COUNT._value.get(),
                "average_response_time": REQUEST_DURATION.observe.sum() / max(REQUEST_COUNT._value.get(), 1),
                "success_rate": 1 - (ERROR_COUNT._value.get() / max(REQUEST_COUNT._value.get(), 1))
            },
            "sessions": {
                "active": await agent_hub.get_active_sessions_count(),
                "total_today": await agent_hub.get_today_sessions_count(),
                "average_duration": await agent_hub.get_average_session_duration()
            },
            "ai_usage": await agent_hub.get_ai_usage_stats(),
            "security": security_manager.get_security_stats()
        }
        
    except Exception as e:
        logging.error(f"Analytics failed: {e}")
        raise HTTPException(status_code=500, detail="Analytics failed")


# 🤖 Include bot routes
app.include_router(bot_router, prefix="/bot")


# 🚨 Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """🚨 HTTP exception handler"""
    ERROR_COUNT.labels(error_type="http").inc()
    
    return {
        "error": {
            "type": "http_error",
            "status_code": exc.status_code,
            "detail": exc.detail,
            "timestamp": asyncio.get_event_loop().time()
        }
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """🚨 General exception handler"""
    ERROR_COUNT.labels(error_type="general").inc()
    
    logging.error(f"Unhandled exception: {exc}")
    
    # Log security event for unhandled exceptions
    security_manager._log_security_event(
        "unhandled_exception",
        None,
        {"error": str(exc), "path": str(request.url)},
        SecurityLevel.HIGH
    )
    
    return {
        "error": {
            "type": "internal_error",
            "status_code": 500,
            "detail": "Internal server error",
            "timestamp": asyncio.get_event_loop().time()
        }
    }


# 📝 Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """📝 Log all requests"""
    start_time = asyncio.get_event_loop().time()
    
    # Log request
    logging.info(f"📥 {request.method} {request.url}")
    
    # Process request
    try:
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
        
        response = await call_next(request)
        
        # Log response
        duration = asyncio.get_event_loop().time() - start_time
        REQUEST_DURATION.observe(duration)
        
        logging.info(f"📤 {request.method} {request.url} - {response.status_code} - {duration:.3f}s")
        
        return response
        
    except Exception as e:
        duration = asyncio.get_event_loop().time() - start_time
        logging.error(f"❌ {request.method} {request.url} - ERROR - {duration:.3f}s - {e}")
        raise


# 🚀 Main function
def main():
    """🚀 Main entry point"""
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(settings.audit_log)
        ]
    )
    
    # Start server
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
        workers=1 if settings.debug else settings.worker_processes,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()
