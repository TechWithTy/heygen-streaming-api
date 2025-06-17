"""
Start session endpoint for the HeyGen Streaming API.

This module provides the route handler for starting an existing streaming session
with the HeyGen API to establish the connection between client and Interactive Avatar.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ...client import client as heygen_client
from ._exceptions import (
    AuthenticationError,
    HeyGenAPIError,
    HeyGenValidationError,
    NotFoundError,
    RateLimitError,
    ServerError,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["streaming"])


class StartSessionRequest(BaseModel):
    """Request model for starting a streaming session."""

    session_id: str = Field(
        ...,
        description="The ID of the session to start",
        example="123456",
        min_length=1,
    )


class StartSessionResponse(BaseModel):
    """Response model for a started streaming session."""

    status: str = Field(
        ...,
        description="The status of the session start operation",
        example="started",
    )


@router.post(
    "/start",
    response_model=StartSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Start a streaming session",
    responses={
        200: {"description": "Session started successfully"},
        400: {"description": "Invalid request data"},
        401: {"description": "Invalid API key"},
        404: {"description": "Session not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Server error"},
    },
)
async def start_streaming_session(
    request: StartSessionRequest,
    # Add any dependencies like authentication here
) -> StartSessionResponse:
    """
    Start an existing streaming session.

    This endpoint activates an existing streaming session and establishes the connection
    between the client and the Interactive Avatar.

    Args:
        request: The session start request containing the session ID

    Returns:
        StartSessionResponse with the status of the operation

    Raises:
        HTTPException: With appropriate status code for any error conditions
    """
    try:
        # Call the HeyGen API to start the session
        response = await heygen_client.start_session(session_id=request.session_id)
        return response

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
    except NotFoundError:
        logger.warning("Session not found: %s", request.session_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Session not found: {request.session_id}"}
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
        logger.exception("Unexpected error in start_streaming_session")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"}
        )