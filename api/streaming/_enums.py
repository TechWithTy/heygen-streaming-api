"""Enums for the HeyGen Streaming API."""
from enum import Enum


class Quality(str, Enum):
    """Quality settings for streaming sessions."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class VideoEncoding(str, Enum):
    """Video encoding formats."""
    H264 = "H264"
    VP8 = "VP8"


class STTProvider(str, Enum):
    """Speech-to-Text providers."""
    DEEPGRAM = "deepgram"
    GLADIA = "gladia"
    ASSEMBLY_AI = "assembly_ai"
