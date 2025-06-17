"""
Create session token functionality for the HeyGen Streaming API.

This module provides functions for creating session tokens for streaming sessions.
"""

from __future__ import annotations

import logging
from typing import Optional

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


class CreateTokenRequest(BaseModel):
    """Request model for creating a session token."""

    session_id: str = Field(..., description="The ID of the session to create a token for")
    expires_in: Optional[int] = Field(
        None,
        description="Optional expiration time in seconds (default: 1 hour)",
        ge=60,
        le=86400,
    )

    @field_validator("session_id")
    def validate_session_id(cls, v: str) -> str:
        """Validate that session_id is a non-empty string."""
        if not v or not v.strip():
            raise ValueError("Session ID cannot be empty")
        return v.strip()


class TokenData(BaseModel):
    """Token data model."""

    token: str = Field(..., description="The session token")


class CreateTokenAPIResponse(BaseModel):
    """API response model for token creation."""

    data: TokenData
    error: Optional[dict] = None


class CreateTokenResponse(BaseModel):
    """Response model for create_session_token."""

    token: str = Field(..., description="The created session token")
    error: Optional[dict] = Field(
        None, description="Error details if the request was not successful"
    )


@router.post(
    "/sessions/{session_id}/tokens",
    response_model=CreateTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a session token",
    responses={
        201: {"description": "Token created successfully"},
        400: {"description": "Invalid request data"},
        401: {"description": "Invalid API key"},
        404: {"description": "Session not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Server error"},
    },
)
async def create_session_token(
    session_id: str,
    expires_in: Optional[int] = 3600,  # 1 hour default
) -> CreateTokenResponse:
    """
    Create a session token for a HeyGen streaming session.

    Args:
        session_id: The ID of the session to create a token for
        expires_in: Optional expiration time in seconds (60-86400, default: 3600)

    Returns:
        CreateTokenResponse containing the session token and any error

    Raises:
        HTTPException: With appropriate status code for any error conditions
    """
    try:
        # Use the HeyGen client to create a session token
        response = await heygen_client.create_session_token(
            session_id=session_id,
            expires_in=expires_in
        )
        
        return CreateTokenResponse(
            token=response.get("data", {}).get("token", ""),
            error=response.get("error")
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
        logger.error(f"API error in create_session_token: {str(e)}")
        raise HTTPException(
            status_code=status_code,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Unexpected error in create_session_token")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )