"""
List active sessions functionality for the HeyGen Streaming API.

This module provides functions for retrieving currently active streaming sessions.
"""

from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

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


class SessionInfo(BaseModel):
    """Model representing an active streaming session."""

    session_id: str = Field(..., description="Unique identifier for the session")
    status: str = Field(..., description="Current status of the session (new/connecting/connected)")
    created_at: int = Field(..., description="Creation time as Unix timestamp")

    @property
    def created_at_dt(self) -> datetime:
        """Return created_at as a datetime object."""
        return datetime.fromtimestamp(self.created_at)


class ListSessionsActiveResponse(BaseModel):
    """Model representing the response for list active sessions."""

    code: int = Field(..., description="Response code")
    message: str = Field(..., description="Response message")
    data: list[SessionInfo] = Field(..., description="List of active sessions")


@router.get(
    "/sessions/active",
    response_model=ListSessionsActiveResponse,
    status_code=status.HTTP_200_OK,
    summary="List active sessions",
    responses={
        200: {"description": "List of active sessions retrieved successfully"},
        400: {"description": "Invalid request data"},
        401: {"description": "Invalid API key"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Server error"},
    },
)
async def list_sessions_active() -> ListSessionsActiveResponse:
    """
    Retrieve a list of currently active streaming sessions.

    This endpoint returns information about all active streaming sessions
    associated with the API key.

    Returns:
        ListSessionsActiveResponse containing the list of active sessions

    Raises:
        HTTPException: With appropriate status code for any error conditions
    """
    try:
        # Use the HeyGen client to list active sessions
        response = await heygen_client.list_active_sessions()
        return ListSessionsActiveResponse(
            code=response.get("code", 100),
            message=response.get("message", "Success"),
            data=[
                SessionInfo(
                    session_id=session.get("session_id"),
                    created_at=session.get("created_at"),
                    status=session.get("status", "ACTIVE")
                )
                for session in response.get("data", [])
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
        logger.exception("Unexpected error in list_active_sessions")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"}
        )