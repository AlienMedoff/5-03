"""
🤖 AI Agent Hub Module
Central management for AI models and agent orchestration
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from core.config import settings, ConfigConstants
from agents.models import AIModelManager
from agents.orchestrator import AgentOrchestrator


class ModelType(Enum):
    """🤖 AI Model types"""
    CLAUDE = "claude"
    MISTRAL = "mistral"
    GROQ = "groq"
    GEMINI = "gemini"


@dataclass
class AIRequest:
    """📋 AI request structure"""
    user_id: int
    message: str
    model: ModelType
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class AIResponse:
    """📋 AI response structure"""
    request: AIRequest
    response: str
    model_used: ModelType
    tokens_used: int
    response_time: float
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class AgentHub:
    """🤖 Central AI Agent Hub"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model_manager = AIModelManager()
        self.orchestrator = AgentOrchestrator()
        self._active_sessions: Dict[str, Dict[str, Any]] = {}
        self._request_history: List[AIRequest] = []
        self._response_history: List[AIResponse] = {}
        
    async def initialize(self):
        """🚀 Initialize the agent hub"""
        try:
            self.logger.info("🤖 Initializing AI Agent Hub...")
            
            # Initialize AI models
            await self.model_manager.initialize()
            
            # Initialize orchestrator
            await self.orchestrator.initialize()
            
            # Load active sessions from storage
            await self._load_sessions()
            
            self.logger.info("✅ AI Agent Hub initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Agent Hub: {e}")
            raise
    
    async def process_request(self, request: AIRequest) -> AIResponse:
        """🔄 Process AI request"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Validate request
            await self._validate_request(request)
            
            # Get or create session
            session_id = await self._get_or_create_session(request.user_id, request.session_id)
            request.session_id = session_id
            
            # Route to appropriate model
            model = await self._route_request(request)
            
            # Process with AI model
            response_content = await self.model_manager.process_request(
                message=request.message,
                model=model,
                context=request.context,
                session_id=session_id
            )
            
            # Create response
            response = AIResponse(
                request=request,
                response=response_content,
                model_used=model,
                tokens_used=self._estimate_tokens(request.message, response_content),
                response_time=asyncio.get_event_loop().time() - start_time
            )
            
            # Store in history
            self._request_history.append(request)
            self._response_history[session_id] = response
            
            # Update session
            await self._update_session(session_id, request, response)
            
            # Cleanup old data
            await self._cleanup_old_data()
            
            self.logger.info(f"✅ Processed request for user {request.user_id} with {model.value}")
            
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Failed to process request: {e}")
            raise
    
    async def _validate_request(self, request: AIRequest):
        """✅ Validate AI request"""
        if not request.message.strip():
            raise ValueError("Message cannot be empty")
        
        if len(request.message) > 10000:  # 10KB limit
            raise ValueError("Message too long")
        
        if request.model not in ModelType:
            raise ValueError(f"Invalid model: {request.model}")
    
    async def _route_request(self, request: AIRequest) -> ModelType:
        """🔄 Route request to appropriate model"""
        # Use specified model if valid
        if request.model in ModelType:
            return request.model
        
        # Use default model
        return ModelType(settings.default_model)
    
    async def _get_or_create_session(self, user_id: int, session_id: Optional[str] = None) -> str:
        """🔍 Get or create session"""
        if session_id and session_id in self._active_sessions:
            return session_id
        
        # Create new session
        new_session_id = f"session_{user_id}_{datetime.now().timestamp()}"
        
        self._active_sessions[new_session_id] = {
            "user_id": user_id,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "message_count": 0,
            "context": {}
        }
        
        return new_session_id
    
    async def _update_session(self, session_id: str, request: AIRequest, response: AIResponse):
        """🔄 Update session data"""
        if session_id not in self._active_sessions:
            return
        
        session = self._active_sessions[session_id]
        session["last_activity"] = datetime.now()
        session["message_count"] += 1
        
        # Update context
        if "conversation" not in session["context"]:
            session["context"]["conversation"] = []
        
        session["context"]["conversation"].append({
            "timestamp": request.timestamp.isoformat(),
            "user_message": request.message,
            "bot_response": response.response,
            "model_used": response.model_used.value,
            "tokens_used": response.tokens_used
        })
        
        # Limit conversation history
        if len(session["context"]["conversation"]) > 50:
            session["context"]["conversation"] = session["context"]["conversation"][-50:]
    
    def _estimate_tokens(self, message: str, response: str) -> int:
        """📊 Estimate token usage"""
        # Rough estimation: ~4 characters per token
        return len(message + response) // 4
    
    async def _load_sessions(self):
        """📂 Load sessions from storage"""
        # TODO: Implement session loading from Redis/database
        pass
    
    async def _cleanup_old_data(self):
        """🧹 Clean up old data"""
        now = datetime.now()
        cutoff_time = now - timedelta(hours=settings.session_timeout)
        
        # Clean up old sessions
        expired_sessions = [
            session_id for session_id, session in self._active_sessions.items()
            if session["last_activity"] < cutoff_time
        ]
        
        for session_id in expired_sessions:
            del self._active_sessions[session_id]
        
        # Clean up old request history
        self._request_history = [
            req for req in self._request_history
            if req.timestamp > cutoff_time
        ]
    
    async def get_session_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """📜 Get session conversation history"""
        if session_id not in self._active_sessions:
            return []
        
        session = self._active_sessions[session_id]
        conversation = session["context"].get("conversation", [])
        
        return conversation[-limit:]
    
    async def get_user_sessions(self, user_id: int) -> List[str]:
        """👤 Get all sessions for a user"""
        return [
            session_id for session_id, session in self._active_sessions.items()
            if session["user_id"] == user_id
        ]
    
    async def delete_session(self, session_id: str) -> bool:
        """🗑️ Delete session"""
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
            if session_id in self._response_history:
                del self._response_history[session_id]
            return True
        return False
    
    async def health_check(self) -> Dict[str, Any]:
        """🏥 Health check for agent hub"""
        try:
            return {
                "status": "healthy",
                "active_sessions": len(self._active_sessions),
                "total_requests": len(self._request_history),
                "models_available": await self.model_manager.get_available_models(),
                "orchestrator_status": await self.orchestrator.get_status()
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def get_status(self) -> Dict[str, Any]:
        """📊 Get detailed status"""
        return {
            "hub": {
                "active_sessions": len(self._active_sessions),
                "total_requests": len(self._request_history),
                "average_response_time": self._calculate_average_response_time(),
                "sessions_per_user": self._calculate_sessions_per_user()
            },
            "models": await self.model_manager.get_status(),
            "orchestrator": await self.orchestrator.get_status()
        }
    
    async def get_active_sessions_count(self) -> int:
        """📊 Get active sessions count"""
        return len(self._active_sessions)
    
    async def get_today_sessions_count(self) -> int:
        """📊 Get today's sessions count"""
        today = datetime.now().date()
        return len([
            session for session in self._active_sessions.values()
            if session["created_at"].date() == today
        ])
    
    async def get_average_session_duration(self) -> float:
        """📊 Get average session duration"""
        if not self._active_sessions:
            return 0.0
        
        now = datetime.now()
        durations = [
            (now - session["created_at"]).total_seconds()
            for session in self._active_sessions.values()
        ]
        
        return sum(durations) / len(durations) if durations else 0.0
    
    async def get_ai_usage_stats(self) -> Dict[str, Any]:
        """📊 Get AI usage statistics"""
        model_usage = {model.value: 0 for model in ModelType}
        total_tokens = 0
        
        for response in self._response_history.values():
            model_usage[response.model_used.value] += 1
            total_tokens += response.tokens_used
        
        return {
            "model_usage": model_usage,
            "total_tokens": total_tokens,
            "average_tokens_per_request": total_tokens / len(self._response_history) if self._response_history else 0,
            "total_requests": len(self._response_history)
        }
    
    def _calculate_average_response_time(self) -> float:
        """📊 Calculate average response time"""
        if not self._response_history:
            return 0.0
        
        response_times = [response.response_time for response in self._response_history.values()]
        return sum(response_times) / len(response_times)
    
    def _calculate_sessions_per_user(self) -> Dict[int, int]:
        """📊 Calculate sessions per user"""
        sessions_per_user = {}
        
        for session in self._active_sessions.values():
            user_id = session["user_id"]
            sessions_per_user[user_id] = sessions_per_user.get(user_id, 0) + 1
        
        return sessions_per_user
    
    async def cleanup(self):
        """🧹 Cleanup resources"""
        try:
            self.logger.info("🧹 Cleaning up Agent Hub...")
            
            # Save sessions
            await self._save_sessions()
            
            # Cleanup model manager
            await self.model_manager.cleanup()
            
            # Cleanup orchestrator
            await self.orchestrator.cleanup()
            
            self.logger.info("✅ Agent Hub cleanup complete")
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup failed: {e}")
    
    async def _save_sessions(self):
        """💾 Save sessions to storage"""
        # TODO: Implement session saving to Redis/database
        pass


# 🌍 Global agent hub instance
agent_hub = AgentHub()
