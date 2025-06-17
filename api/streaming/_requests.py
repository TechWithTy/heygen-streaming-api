"""Request models and validation for the HeyGen Streaming API."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class AvatarStyle(str, Enum):
    """Available avatar styles."""
    REALISTIC = "realistic"
    CARTOON = "cartoon"
    ANIME = "anime"


class VoiceSettings(BaseModel):
    """Voice settings for the avatar."""
    voice_id: str = Field(..., description="ID of the voice to use")
    speed: float = Field(1.0, ge=0.5, le=2.0, description="Speech rate (0.5-2.0)")
    pitch: float = Field(1.0, ge=0.5, le=2.0, description="Voice pitch (0.5-2.0)")
    volume: float = Field(1.0, ge=0.0, le=1.0, description="Volume level (0.0-1.0)")


class AvatarSettings(BaseModel):
    """Avatar configuration settings."""
    avatar_id: str = Field(..., description="ID of the avatar to use")
    style: AvatarStyle = Field(AvatarStyle.REALISTIC, description="Avatar style")
    background_color: str = Field("#000000", description="Background color in hex")
    size: dict[str, int] = Field(
        {"width": 1920, "height": 1080},
        description="Video dimensions in pixels"
    )


class TextInput(BaseModel):
    """Text input for avatar speech."""
    text: str = Field(..., description="Text to be spoken")
    voice: VoiceSettings | None = Field(None, description="Voice configuration")


class AudioInput(BaseModel):
    """Audio input for lip-syncing."""
    audio_url: str = Field(..., description="URL of the audio file")
    voice: VoiceSettings | None = Field(None, description="Voice configuration")


class NewSessionRequest(BaseModel):
    """Request model for creating a new streaming session."""
    avatar: AvatarSettings = Field(..., description="Avatar configuration")
    script: TextInput | AudioInput = Field(..., description="Input script or audio")
    session_id: str | None = Field(
        None,
        description="Custom session ID. If not provided, one will be generated."
    )
    metadata: dict[str, Any] | None = Field(
        None,
        description="Additional metadata to store with the session"
    )

    @field_validator('script', mode='before')
    @classmethod
    def validate_script(cls, v: Any) -> Any:
        """Validate script input."""
        if not v:
            raise ValueError("Script cannot be empty")
        return v


def validate_new_session_request(data: dict) -> dict:
    """Validate and normalize new session request data.

    Args:
        data: Dictionary containing the request data
    Returns:
        dict: Validated and normalized request data
    Raises:
        HeyGenValidationError: If validation fails
    """
    from pydantic import ValidationError

    from ._exceptions import HeyGenValidationError

    try:
        # Convert to Pydantic model for validation
        request = NewSessionRequest.model_validate(data)
        # Convert back to dict, excluding unset values
        return request.model_dump(exclude_none=True)
    except ValidationError as e:
        raise HeyGenValidationError(
            message="Invalid request data",
            details={"validation_errors": e.errors()}
        ) from e
