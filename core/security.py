"""
🔒 Security Module
Enterprise-level security for Aether Multi-Agent Bot
"""

import hashlib
import hmac
import time
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .config import settings


class SecurityLevel(Enum):
    """🔐 Security levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    """🚨 Alert types"""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SECURITY_BREACH = "security_breach"
    SYSTEM_ERROR = "system_error"


@dataclass
class SecurityEvent:
    """📋 Security event"""
    event_type: str
    user_id: Optional[int]
    timestamp: datetime
    ip_address: Optional[str]
    details: Dict[str, Any]
    severity: SecurityLevel


class SecurityManager:
    """🛡️ Security Manager"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._failed_attempts: Dict[int, List[datetime]] = {}
        self._rate_limits: Dict[int, List[datetime]] = {}
        self._security_events: List[SecurityEvent] = []
        
    def verify_user(self, user_id: int) -> bool:
        """✅ Verify user access"""
        try:
            # Check if user is allowed
            if user_id not in settings.allowed_users:
                self._log_security_event(
                    "unauthorized_access_attempt",
                    user_id,
                    {"allowed_users": settings.allowed_users},
                    SecurityLevel.HIGH
                )
                return False
            
            # Check if user is locked out
            if self._is_user_locked_out(user_id):
                self._log_security_event(
                    "locked_out_access_attempt",
                    user_id,
                    {"lockout_reason": "too_many_failed_attempts"},
                    SecurityLevel.MEDIUM
                )
                return False
            
            # Check rate limit
            if self._is_rate_limited(user_id):
                self._log_security_event(
                    "rate_limit_exceeded",
                    user_id,
                    {"rate_limit": settings.rate_limit},
                    SecurityLevel.MEDIUM
                )
                return False
            
            # Reset failed attempts on successful access
            self._reset_failed_attempts(user_id)
            return True
            
        except Exception as e:
            self.logger.error(f"Security verification error: {e}")
            return False
    
    def _is_user_locked_out(self, user_id: int) -> bool:
        """🔒 Check if user is locked out"""
        if user_id not in self._failed_attempts:
            return False
        
        # Count failed attempts in the last 5 minutes
        now = datetime.now()
        recent_attempts = [
            attempt for attempt in self._failed_attempts[user_id]
            if now - attempt < timedelta(minutes=5)
        ]
        
        return len(recent_attempts) >= 3
    
    def _is_rate_limited(self, user_id: int) -> bool:
        """⏱️ Check if user is rate limited"""
        if user_id not in self._rate_limits:
            self._rate_limits[user_id] = []
        
        now = datetime.now()
        window_start = now - timedelta(seconds=settings.rate_limit_window)
        
        # Count requests in the time window
        recent_requests = [
            req_time for req_time in self._rate_limits[user_id]
            if req_time > window_start
        ]
        
        # Update rate limit tracking
        self._rate_limits[user_id] = recent_requests + [now]
        
        return len(recent_requests) >= settings.rate_limit
    
    def _reset_failed_attempts(self, user_id: int):
        """🔄 Reset failed attempts for user"""
        if user_id in self._failed_attempts:
            del self._failed_attempts[user_id]
    
    def _log_security_event(self, event_type: str, user_id: Optional[int], 
                          details: Dict[str, Any], severity: SecurityLevel):
        """📝 Log security event"""
        event = SecurityEvent(
            event_type=event_type,
            user_id=user_id,
            timestamp=datetime.now(),
            ip_address=None,  # Could be added from request context
            details=details,
            severity=severity
        )
        
        self._security_events.append(event)
        
        # Log to file
        log_level = {
            SecurityLevel.LOW: logging.INFO,
            SecurityLevel.MEDIUM: logging.WARNING,
            SecurityLevel.HIGH: logging.ERROR,
            SecurityLevel.CRITICAL: logging.CRITICAL
        }.get(severity, logging.INFO)
        
        self.logger.log(
            log_level,
            f"Security Event: {event_type} | User: {user_id} | Details: {details}"
        )
        
        # Trigger alert if critical
        if severity in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
            self._trigger_alert(event)
    
    def _trigger_alert(self, event: SecurityEvent):
        """🚨 Trigger security alert"""
        try:
            # Log to audit file
            with open(settings.audit_log, "a", encoding="utf-8") as f:
                f.write(
                    f"{event.timestamp.isoformat()} | SECURITY_ALERT | "
                    f"{event.event_type} | User: {event.user_id} | "
                    f"Severity: {event.severity.value} | Details: {event.details}\n"
                )
            
            # TODO: Send Telegram alert
            # await self._send_telegram_alert(event)
            
        except Exception as e:
            self.logger.error(f"Failed to trigger security alert: {e}")
    
    def generate_secure_token(self, data: str) -> str:
        """🔐 Generate secure token"""
        return hmac.new(
            settings.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def verify_token(self, data: str, token: str) -> bool:
        """✅ Verify secure token"""
        expected_token = self.generate_secure_token(data)
        return hmac.compare_digest(expected_token, token)
    
    def hash_sensitive_data(self, data: str) -> str:
        """🔒 Hash sensitive data"""
        return hashlib.sha256(
            (data + settings.secret_key).encode()
        ).hexdigest()
    
    def get_security_stats(self) -> Dict[str, Any]:
        """📊 Get security statistics"""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        
        recent_events = [
            event for event in self._security_events
            if event.timestamp > last_24h
        ]
        
        return {
            "total_events": len(self._security_events),
            "last_24h_events": len(recent_events),
            "failed_attempts": len(self._failed_attempts),
            "rate_limited_users": len(self._rate_limits),
            "locked_out_users": len([
                user_id for user_id in self._failed_attempts.keys()
                if self._is_user_locked_out(user_id)
            ]),
            "security_level": self._calculate_security_level(),
            "last_event": self._security_events[-1].timestamp.isoformat() if self._security_events else None
        }
    
    def _calculate_security_level(self) -> str:
        """🔍 Calculate current security level"""
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        
        recent_critical = len([
            event for event in self._security_events
            if event.timestamp > last_hour and event.severity == SecurityLevel.CRITICAL
        ])
        
        recent_high = len([
            event for event in self._security_events
            if event.timestamp > last_hour and event.severity == SecurityLevel.HIGH
        ])
        
        if recent_critical > 0:
            return "CRITICAL"
        elif recent_high > 2:
            return "HIGH"
        elif recent_high > 0:
            return "MEDIUM"
        else:
            return "LOW"
    
    def cleanup_old_data(self):
        """🧹 Clean up old security data"""
        now = datetime.now()
        cutoff_time = now - timedelta(days=7)  # Keep 7 days of data
        
        # Clean up old failed attempts
        for user_id in list(self._failed_attempts.keys()):
            self._failed_attempts[user_id] = [
                attempt for attempt in self._failed_attempts[user_id]
                if attempt > cutoff_time
            ]
            if not self._failed_attempts[user_id]:
                del self._failed_attempts[user_id]
        
        # Clean up old rate limits
        for user_id in list(self._rate_limits.keys()):
            self._rate_limits[user_id] = [
                req_time for req_time in self._rate_limits[user_id]
                if req_time > cutoff_time
            ]
            if not self._rate_limits[user_id]:
                del self._rate_limits[user_id]
        
        # Clean up old security events
        self._security_events = [
            event for event in self._security_events
            if event.timestamp > cutoff_time
        ]


# 🌍 Global security manager instance
security_manager = SecurityManager()


# 🔐 Decorators for security
def require_auth(func):
    """🔒 Require authentication decorator"""
    async def wrapper(*args, **kwargs):
        # Extract user_id from arguments (implementation depends on framework)
        user_id = kwargs.get('user_id') or args[0] if args else None
        
        if user_id is None:
            raise ValueError("User ID required for authentication")
        
        if not security_manager.verify_user(user_id):
            raise PermissionError("Access denied")
        
        return await func(*args, **kwargs)
    
    return wrapper


def rate_limit(limit: int = 10, window: int = 60):
    """⏱️ Rate limiting decorator"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id') or args[0] if args else None
            
            if user_id is None:
                raise ValueError("User ID required for rate limiting")
            
            if security_manager._is_rate_limited(user_id):
                raise PermissionError("Rate limit exceeded")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def log_security_event(event_type: str, severity: SecurityLevel = SecurityLevel.MEDIUM):
    """📝 Log security event decorator"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id') or args[0] if args else None
            
            try:
                result = await func(*args, **kwargs)
                
                security_manager._log_security_event(
                    f"{event_type}_success",
                    user_id,
                    {"function": func.__name__},
                    severity
                )
                
                return result
                
            except Exception as e:
                security_manager._log_security_event(
                    f"{event_type}_error",
                    user_id,
                    {"function": func.__name__, "error": str(e)},
                    SecurityLevel.HIGH
                )
                raise
        
        return wrapper
    return decorator
