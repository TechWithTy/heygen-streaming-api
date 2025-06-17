"""
List avatars functionality for the HeyGen Streaming API.

This module provides functions for retrieving a list of public and custom interactive avatars.
"""

from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from ...client import client as heygen_client
from ._exceptions import (
    AuthenticationError,
    HeyGenAPIError,
    HeyGenValidationError,
    RateLimitError,
    ServerError,
)

router = APIRouter(tags=["streaming"])

logger = logging.getLogger(__name__)


class AvatarInfo(BaseModel):
    """Model representing an avatar's information."""

    avatar_id: str = Field(..., description="Unique identifier for the avatar")
    created_at: int = Field(..., description="Timestamp when the avatar was created")
    is_public: bool = Field(..., description="Whether the avatar is public")
    status: str = Field(..., description="Current status of the avatar (e.g., ACTIVE, INACTIVE)")

    @property
    def created_at_dt(self) -> datetime:
        """Return created_at as a datetime object."""
        return datetime.fromtimestamp(self.created_at)

    @field_validator("status")
    def validate_status(cls, v: str) -> str:
        """Validate that status is a non-empty string."""
        if not v or not v.strip():
            raise ValueError("Status cannot be empty")
        return v.strip().upper()


class ListAvatarsResponse(BaseModel):
    """Response model for listing avatars."""

    code: int = Field(..., description="Status code of the response (e.g., 100 for success)")
    message: str = Field(..., description="Response message")
    data: list[AvatarInfo] = Field(default_factory=list, description="List of avatar objects")

    @field_validator("code")
    def validate_code(cls, v: int) -> int:
        """Validate that code is a positive integer."""
        if v < 0:
            raise ValueError("Code must be a positive integer")
        return v

    @field_validator("message")
    def validate_message(cls, v: str) -> str:
        """Validate that message is a non-empty string."""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


@router.get(
    "/avatars",
    response_model=ListAvatarsResponse,
    status_code=status.HTTP_200_OK,
    summary="List available avatars",
    responses={
        200: {"description": "List of avatars retrieved successfully"},
        400: {"description": "Invalid request data"},
        401: {"description": "Invalid API key"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Server error"},
    },
)
async def list_avatars() -> ListAvatarsResponse:
    """
    Retrieve a list of public and custom interactive avatars.

    This endpoint returns a paginated list of available avatars that can be used
    for streaming sessions.

    Returns:
        ListAvatarsResponse containing the list of available avatars

    Raises:
        HTTPException: With appropriate status code for any error conditions
    """
    try:
        # Use the HeyGen client to list avatars
        response = await heygen_client.list_avatars()
        return ListAvatarsResponse(
            code=response.get("code", 100),
            message=response.get("message", "Success"),
            data=[
                AvatarInfo(
                    avatar_id=avatar.get("avatar_id"),
                    created_at=avatar.get("created_at"),
                    is_public=avatar.get("is_public", True),
                    status=avatar.get("status", "ACTIVE")
                )
                for avatar in response.get("data", [])
            ]
        )

    except HeyGenValidationError as e:
        logger.warning("Validation error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": str(e), "details": getattr(e, "details", {})}
        )
    except AuthenticationError as e:
        logger.warning("Authentication failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": str(e)}
        )
    except RateLimitError as e:
        logger.warning("Rate limit exceeded")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"message": str(e)}
        )
    except (ServerError, HeyGenAPIError) as e:
        logger.error("API error: %s", str(e))
        raise HTTPException(
            status_code=getattr(e, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
            detail={"message": str(e), "details": getattr(e, "details", {})}
        )
    except Exception:
        logger.exception("Unexpected error in list_avatars")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"}
        )