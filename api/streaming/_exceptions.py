"""Exceptions for the HeyGen Streaming API."""


class HeyGenAPIError(Exception):
    """Base exception for all HeyGen API errors."""
    def __init__(self, message=None, status_code=None, details=None):
        self.message = message or "An error occurred with the HeyGen API"
        self.status_code = status_code or 500
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(HeyGenAPIError):
    """Raised when authentication fails."""
    def __init__(self, message="Authentication failed"):
        super().__init__(message=message, status_code=401)


class HeyGenValidationError(HeyGenAPIError):
    """Raised when request validation fails."""
    def __init__(self, message: str = "Invalid request data", details: dict | None = None):
        super().__init__(
            message=message,
            status_code=400,
            details=details or {}
        )


class ValidationError(HeyGenValidationError):
    """Legacy alias for HeyGenValidationError."""
    pass


class RateLimitError(HeyGenAPIError):
    """Raised when rate limits are exceeded."""
    def __init__(self, message="Rate limit exceeded"):
        super().__init__(message=message, status_code=429)


class NotFoundError(HeyGenAPIError):
    """Raised when a resource is not found."""
    def __init__(self, message="Resource not found"):
        super().__init__(message=message, status_code=404)


class ServerError(HeyGenAPIError):
    """Raised when a server error occurs."""
    def __init__(self, message="Internal server error"):
        super().__init__(message=message, status_code=500)


class SessionNotFoundError(NotFoundError):
    """Raised when a streaming session is not found or no longer active.

    This is a more specific type of NotFoundError that indicates the requested
    streaming session either doesn't exist or is no longer active.
    """
    def __init__(self, message: str = "Streaming session not found or no longer active"):
        super().__init__(message=message)

