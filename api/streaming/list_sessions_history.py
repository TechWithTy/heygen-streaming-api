"""
List sessions history functionality for the HeyGen Streaming API.

This module provides functions for retrieving a paginated history of all streaming sessions,
including metadata such as session duration, timestamps, and other details.
"""

from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status
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


class SessionHistoryInfo(BaseModel):
    """Model representing a single historical session entry."""
    session_id: str = Field(..., description="Unique identifier for the session")
    created_at: int = Field(..., description="Creation time as Unix timestamp")
    ended_at: int | None = Field(None, description="End time as Unix timestamp")
    status: str = Field("COMPLETED", description="Status of the session")
    duration_seconds: int = Field(0, description="Duration of the session in seconds")
    avatar_id: str | None = Field(None, description="ID of the avatar used")
    voice_name: str | None = Field(None, description="Name of the voice used")

    @property
    def created_at_dt(self) -> datetime:
        """Return created_at as a datetime object."""
        return datetime.fromtimestamp(self.created_at)

    @property
    def ended_at_dt(self) -> datetime | None:
        """Return ended_at as a datetime object if available."""
        return datetime.fromtimestamp(self.ended_at) if self.ended_at else None


class PaginationInfo(BaseModel):
    """Model for pagination information in the response."""
    total: int = Field(0, description="Total number of items")
    limit: int = Field(10, description="Number of items per page")
    offset: int = Field(0, description="Pagination offset")
    has_more: bool = Field(False, description="Whether there are more items available")


class ListSessionsHistoryResponse(BaseModel):
    """Response model for the list sessions history endpoint."""
    code: int = Field(100, description="Response status code")
    message: str = Field("Success", description="Response message")
    data: list[SessionHistoryInfo] = Field(default_factory=list, description="List of session history items")
    pagination: PaginationInfo = Field(..., description="Pagination information")


@router.get(
    "/sessions/history",
    response_model=ListSessionsHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="List historical sessions",
    responses={
        200: {"description": "List of historical sessions retrieved successfully"},
        400: {"description": "Invalid request data"},
        401: {"description": "Invalid API key"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Server error"},
    },
)
async def list_sessions_history(
    start_time: int | None = Query(
        None,
        description="Unix timestamp for the start of the time range",
        example=1672531200,
    ),
    end_time: int | None = Query(
        None,
        description="Unix timestamp for the end of the time range",
        example=1672617600,
    ),
    limit: int = Query(
        10,
        description="Maximum number of sessions to return",
        ge=1,
        le=100,
    ),
    offset: int = Query(0, description="Pagination offset", ge=0),
) -> ListSessionsHistoryResponse:
    """
    Retrieve a paginated list of historical streaming sessions.

    This endpoint returns information about past streaming sessions within the
    specified time range, with support for pagination.

    Args:
        start_time: Optional start time filter (unix timestamp)
        end_time: Optional end time filter (unix timestamp)
        limit: Maximum number of sessions to return (1-100)
        offset: Pagination offset

    Returns:
        ListSessionsHistoryResponse containing paginated session history

    Raises:
        HTTPException: With appropriate status code for any error conditions
    """
    try:
        # Use the HeyGen client to list session history
        response = await heygen_client.list_sessions_history(
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset
        )
        
        # Transform the response using Pydantic models
        return ListSessionsHistoryResponse(
            code=response.get("code", 100),
            message=response.get("message", "Success"),
            data=[
                SessionHistoryInfo(
                    session_id=session["session_id"],
                    created_at=session["created_at"],
                    ended_at=session.get("ended_at"),
                    status=session.get("status", "COMPLETED"),
                    duration_seconds=session.get("duration_seconds", 0),
                    avatar_id=session.get("avatar_id"),
                    voice_name=session.get("voice_name")
                )
                for session in response.get("data", [])
                if "session_id" in session and "created_at" in session
            ],
            pagination=PaginationInfo(
                total=response.get("pagination", {}).get("total", 0),
                limit=limit,
                offset=offset,
                has_more=response.get("pagination", {}).get("has_more", False)
            )
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
        logger.exception("Unexpected error in list_sessions_history")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"}
        )