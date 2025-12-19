"""Rate limiting utilities with testing support."""
import os
from functools import wraps
from typing import Callable, Any

# Rate limiting is disabled during testing
TESTING = os.getenv("TESTING", "false").lower() == "true"


def conditional_rate_limit(limiter, rate: str):
    """
    Apply rate limiting conditionally - disabled during testing.

    Args:
        limiter: The slowapi Limiter instance
        rate: Rate string (e.g., "5/minute")

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        if TESTING:
            # Return the function unchanged during tests
            return func
        else:
            # Apply rate limiting in production
            return limiter.limit(rate)(func)
    return decorator