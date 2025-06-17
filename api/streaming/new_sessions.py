"""
New session creation endpoint for the HeyGen Streaming API.

This module provides the request/response models and route handlers for creating
new streaming sessions with the HeyGen API.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError

from ...client import client as heygen_client
from ._exceptions import (
    AuthenticationError,
    HeyGenAPIError,
    HeyGenValidationError,
    NotFoundError,
    RateLimitError,
    ServerError,
)
from ._requests import NewSessionRequest, validate_new_session_request
from ._responses import NewSessionResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/streaming", tags=["streaming"])

@router.post(
    "/sessions",
    response_model=NewSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new streaming session",
    responses={
        201: {"description": "Session created successfully"},
        400: {"description": "Invalid request data"},
        401: {"description": "Invalid API key"},
        404: {"description": "Resource not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Server error"},
    },
)
async def create_streaming_session(
    request: NewSessionRequest,
    # Add any dependencies like authentication here
) -> NewSessionResponse:
    """
    Create a new streaming session with the specified settings.

    This endpoint creates a new streaming session with the provided configuration.

    Args:
        request: The session configuration

    Returns:
        NewSessionResponse with session details

    Raises:
        HTTPException: With appropriate status code for any error conditions
    """
    try:
        # Validate the request data
        validate_new_session_request(request.model_dump(exclude_none=True))
        
        # Call the HeyGen API to create a new session
        response = await heygen_client.create_session(request)
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
    except NotFoundError as e:
        logger.warning("Resource not found: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": str(e), "details": getattr(e, "details", {})}
        )
    except ValidationError as e:
        logger.warning("Request validation failed: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Validation error", "details": str(e)}
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
    except Exception as e:
        logger.exception("Unexpected error in create_streaming_session")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"}
        )