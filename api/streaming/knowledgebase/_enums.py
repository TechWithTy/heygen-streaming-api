"""
Enums for the HeyGen Knowledge Base API.

This module contains all the enumerations used across the knowledge base API.
"""

from enum import Enum


class KnowledgeBaseStatus(str, Enum):
    """Status of a knowledge base."""
    ACTIVE = "ACTIVE"
    PROCESSING = "PROCESSING"
    FAILED = "FAILED"
    DELETING = "DELETING"

class DocumentStatus(str, Enum):
    """Status of a document within a knowledge base."""
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
