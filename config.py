"""Configuration for HeyGen Streaming API integration."""

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class HeyGenStreamingConfig(BaseSettings):
    """Configuration for HeyGen Streaming API.
    
    Loads settings from environment variables with the prefix 'HEYGEN_'.
    """
    
    # API Configuration
    API_KEY: str = Field(..., description="HeyGen API key")
    BASE_URL: str = Field(
        "https://api.heygen.com/v1",
        description="Base URL for the HeyGen API"
    )
    TIMEOUT: int = Field(
        30,
        description="Request timeout in seconds"
    )
    
    # Model configuration
    model_config = SettingsConfigDict(
        env_prefix="HEYGEN_",
        env_file=".env",
        extra="ignore",
        case_sensitive=True,
    )


@lru_cache()
def get_config() -> HeyGenStreamingConfig:
    """Get cached HeyGen Streaming configuration.
    
    Returns:
        HeyGenStreamingConfig: The configuration instance
    """
    return HeyGenStreamingConfig()


# Global config instance
config = get_config()