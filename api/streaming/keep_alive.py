"""
Keep-alive functionality for the HeyGen Streaming API.

This module provides functions for resetting the idle-timeout countdown
for an active streaming session.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from ...client import client as heygen_client
from ._exceptions import (
    AuthenticationError,
    HeyGenAPIError,
    RateLimitError,
    ServerError,
    SessionNotFoundError,
)

router = APIRouter(tags=["streaming"])
logger = logging.getLogger(__name__)


class KeepAliveResponse(BaseModel):
    """Response model for keep-alive operation."""

    code: int = Field(..., description="The response status code")
    message: str = Field(..., description="Details about the request's result")

    @field_validator("code")
    def validate_code(cls, v: int) -> int:
        """Validate that code is a non-negative integer."""
        if v < 0:
            raise ValueError("Code must be a non-negative integer")
        return v

    @field_validator("message")
    def validate_message(cls, v: str) -> str:
        """Validate that message is a non-empty string."""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


class KeepAliveRequest(BaseModel):
    """Request model for keep-alive operation."""

    session_id: str = Field(..., description="The ID of the session to keep alive")

    @field_validator("session_id")
    def validate_session_id(cls, v: str) -> str:
        """Validate that session_id is a non-empty string."""
        if not v or not v.strip():
            raise ValueError("Session ID cannot be empty")
        return v.strip()


@router.post(
    "/sessions/{session_id}/keepalive",
    response_model=KeepAliveResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset session idle timeout",
    responses={
        200: {"description": "Keep-alive signal sent successfully"},
        400: {"description": "Invalid request data"},
        401: {"description": "Invalid API key"},
        404: {"description": "Session not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Server error"},
    },
)
async def keep_alive(
    session_id: str,
) -> KeepAliveResponse:
    """
    Reset the idle-timeout countdown for an active streaming session.

    Args:
        session_id: The ID of the session to keep alive

    Returns:
        KeepAliveResponse containing the operation status

    Raises:
        HTTPException: With appropriate status code for any error conditions
    """
    try:
        # Use the HeyGen client to send keep-alive signal
        response = await heygen_client.keep_alive(session_id=session_id)
        
        return KeepAliveResponse(
            code=response.get("code", 0),
            message=response.get("message", "Keep-alive signal sent successfully")
        )

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except SessionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except (ServerError, HeyGenAPIError) as e:
        status_code = getattr(e, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.error(f"API error in keep_alive: {str(e)}")
        raise HTTPException(
            status_code=status_code,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Unexpected error in keep_alive")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )