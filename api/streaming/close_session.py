"""
Close session functionality for the HeyGen Streaming API.

This module provides functions for terminating an active streaming session.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

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


class CloseSessionResponse(BaseModel):
    """Response model for closing a session."""

    status: str = Field(..., description="Status of the close operation (success/failure)")


@router.post(
    "/sessions/{session_id}/close",
    response_model=CloseSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Close a streaming session",
    responses={
        200: {"description": "Session closed successfully"},
        401: {"description": "Invalid API key"},
        404: {"description": "Session not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Server error"},
    },
)
async def close_session(
    session_id: str,
) -> CloseSessionResponse:
    """
    Terminate an active streaming session.

    Args:
        session_id: The ID of the session to be stopped

    Returns:
        CloseSessionResponse containing the status of the operation

    Raises:
        HTTPException: With appropriate status code for any error conditions
    """
    try:
        # Use the HeyGen client to close the session
        response = await heygen_client.close_session(session_id=session_id)
        
        return CloseSessionResponse(status=response.get("status", "success"))

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
        logger.error(f"API error in close_session: {str(e)}")
        raise HTTPException(
            status_code=status_code,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Unexpected error in close_session")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
