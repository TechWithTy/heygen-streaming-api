"""
Send task functionality for the HeyGen Streaming API.

This module provides functions for sending text tasks to an Interactive Avatar,
prompting it to speak the provided text either synchronously or asynchronously.
"""

from __future__ import annotations

import logging
from enum import Enum

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from ...client import client as heygen_client
from ._exceptions import (
    AuthenticationError,
    HeyGenAPIError,
    HeyGenValidationError,
    RateLimitError,
    ServerError,
    SessionNotFoundError,
)

router = APIRouter(tags=["streaming"])

logger = logging.getLogger(__name__)


class TaskMode(str, Enum):
    """Available task modes for sending tasks to the avatar."""

    SYNC = "sync"
    ASYNC = "async"


class TaskType(str, Enum):
    """Available task types for the avatar."""

    REPEAT = "repeat"  # Simply repeat the input text
    CHAT = "chat"  # Respond according to knowledge base


class TaskResponse(BaseModel):
    """Response model for a sent task."""

    duration_ms: float = Field(..., description="Duration of the avatar's speech in milliseconds")
    task_id: str = Field(..., description="Unique identifier for the task")


class SendTaskRequest(BaseModel):
    """Request model for sending a task to the avatar."""

    session_id: str = Field(..., description="The ID of the target session")
    text: str = Field(..., min_length=1, description="The text for the avatar to speak")
    task_mode: TaskMode = Field(
        default=TaskMode.SYNC,
        description="Whether the task is performed synchronously or asynchronously",
    )
    task_type: TaskType = Field(
        default=TaskType.REPEAT,
        description="Type of task (repeat or chat with knowledge base)",
    )

    @field_validator("text")
    def validate_text(cls, v: str) -> str:
        """Validate that the text is not empty after stripping whitespace."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Text cannot be empty or whitespace")
        return stripped


@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a task to an existing streaming session",
    responses={
        200: {"description": "Task sent successfully"},
        400: {"description": "Invalid request data"},
        401: {"description": "Invalid API key"},
        404: {"description": "Session not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Server error"},
    },
)
async def send_task(
    request: SendTaskRequest,
) -> TaskResponse:
    """
    Send a text task to an Interactive Avatar.

    This endpoint sends a text task to an existing streaming session, which can be
    processed either synchronously or asynchronously.

    Args:
        request: The task request containing session ID, text, and task parameters

    Returns:
        TaskResponse with task ID and duration

    Raises:
        HTTPException: With appropriate status code for any error conditions
    """
    try:
        # Call the HeyGen API to send the task
        response = await heygen_client.send_task(request)
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
    except SessionNotFoundError as e:
        logger.warning("Session not found: %s", request.session_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
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
        logger.exception("Unexpected error in send_task")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"}
        )