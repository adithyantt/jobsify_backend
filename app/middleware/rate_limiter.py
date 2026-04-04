"""
Simple in-memory rate limiter for FastAPI
"""
import time
from collections import defaultdict
from fastapi import HTTPException, Request


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.locked_ips = {}
    
    def check_rate_limit(self, key: str, max_requests: int = 5, window_seconds: int = 60):
        """
        Check if key has exceeded rate limit
        Args:
            key: Unique identifier (IP address or user email)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        now = time.time()
        
        # Check if IP is locked
        if key in self.locked_ips:
            if time.time() < self.locked_ips[key]:
                raise HTTPException(
                    status_code=429,
                    detail="Too many attempts. Please try again later."
                )
            else:
                # Unlock the IP
                del self.locked_ips[key]
        
        # Clean old requests
        self.requests[key] = [t for t in self.requests[key] if now - t < window_seconds]
        
        # Check if limit exceeded
        if len(self.requests[key]) >= max_requests:
            # Lock for 5 minutes
            self.locked_ips[key] = now + 300
            raise HTTPException(
                status_code=429,
                detail="Too many attempts. Please try again later."
            )
        
        # Add current request
        self.requests[key].append(now)
    
    def reset(self, key: str):
        """Reset rate limit for a key"""
        if key in self.requests:
            del self.requests[key]
        if key in self.locked_ips:
            del self.locked_ips[key]


# Global rate limiter instance
rate_limiter = RateLimiter()


def check_login_rate_limit(email: str):
    """Check rate limit for login attempts"""
    rate_limiter.check_rate_limit(f"login:{email}", max_requests=5, window_seconds=60)


def check_register_rate_limit(email: str):
    """Check rate limit for registration attempts"""
    rate_limiter.check_rate_limit(f"register:{email}", max_requests=3, window_seconds=300)


def check_otp_rate_limit(email: str):
    """Check rate limit for OTP requests"""
    rate_limiter.check_rate_limit(f"otp:{email}", max_requests=3, window_seconds=300)
