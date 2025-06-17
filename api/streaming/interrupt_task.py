"""
Interrupt task functionality for the HeyGen Streaming API.

This module provides functions for interrupting the speech of an Interactive Avatar.
If the avatar is not speaking when the API is called, the interrupt has no effect.
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

class InterruptTaskResponse(BaseModel):
    """Response model for interrupt task operation."""

    success: bool = Field(..., description="Whether the interrupt was successful")
    message: str = Field(..., description="Status message")


@router.post(
    "/sessions/{session_id}/interrupt",
    response_model=InterruptTaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Interrupt current speech",
    responses={
        200: {"description": "Interrupt signal sent successfully"},
        400: {"description": "Invalid request data"},
        401: {"description": "Invalid API key"},
        404: {"description": "Session not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Server error"},
    },
)
async def interrupt_task(
    session_id: str,
) -> InterruptTaskResponse:
    """
    Interrupt the current speech of an Interactive Avatar.

    Args:
        session_id: The ID of the session to interrupt

    Returns:
        InterruptTaskResponse indicating success/failure

    Raises:
        HTTPException: With appropriate status code for any error conditions
    """
    try:
        # Use the HeyGen client to send interrupt signal
        await heygen_client.interrupt_task(session_id=session_id)
        
        return InterruptTaskResponse(
            success=True,
            message="Interrupt signal sent successfully"
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
        logger.error(f"API error in interrupt_task: {str(e)}")
        raise HTTPException(
            status_code=status_code,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Unexpected error in interrupt_task")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )