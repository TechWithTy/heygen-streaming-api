"""Response models for the HeyGen Streaming API."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SessionStatus(str, Enum):
    """Status of a streaming session."""
    CREATED = "created"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    EXPIRED = "expired"


class SessionStats(BaseModel):
    """Statistics about a streaming session."""
    duration_seconds: float | None = Field(None, description="Duration of the session in seconds")
    processed_frames: int = Field(..., description="Number of frames processed")
    start_time: datetime = Field(..., description="When processing started")
    end_time: datetime | None = Field(None, description="When processing completed")


class SessionOutput(BaseModel):
    """Output details for a streaming session."""
    video_url: str | None = Field(None, description="URL to download the generated video")
    thumbnail_url: str | None = Field(None, description="URL to the video thumbnail")
    audio_url: str | None = Field(None, description="URL to the generated audio")
    subtitles_url: str | None = Field(None, description="URL to the generated subtitles (VTT)")


class NewSessionResponse(BaseModel):
    """Response model for creating a new streaming session."""
    session_id: str = Field(..., description="Unique identifier for the session")
    status: SessionStatus = Field(..., description="Current status of the session")
    created_at: datetime = Field(..., description="When the session was created")
    expires_at: datetime | None = Field(
        None,
        description="When the session will expire"
    )
    output: SessionOutput | None = Field(
        None,
        description="Output details, available when processing is complete"
    )
    stats: SessionStats | None = Field(
        None,
        description="Processing statistics, available during/after processing"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata associated with the session"
    )


class ErrorResponse(BaseModel):
    """Standard error response from the API."""
    error: str | None = Field(None, description="Error message")
    code: int = Field(..., description="Error code")
    details: dict[str, Any] | None = Field(
        None,
        description="Additional error details"
    )


class ListSessionsResponse(BaseModel):
    """Response model for listing sessions."""
    sessions: list[NewSessionResponse] = Field(
        default_factory=list,
        description="List of sessions"
    )
    next_page_token: str | None = Field(
        None,
        description="Token for the next page of results"
    )
