"""
Request models for the HeyGen Knowledge Base API.

This module contains all the request models used in the knowledge base API.
"""

from pydantic import BaseModel, Field, field_validator


class ListKnowledgeBasesRequest(BaseModel):
    """Request model for listing knowledge bases."""
    
    # No parameters needed for listing, but we keep this for consistency
    pass

class CreateKnowledgeBaseRequest(BaseModel):
    """Request model for creating a knowledge base."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Name of the knowledge base")
    opening: str = Field(..., description="Opening line or introduction for the knowledge base")
    prompt: str = Field(..., description="Custom prompt for the knowledge base")
    
    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        """Validate the knowledge base name."""
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v

class UpdateKnowledgeBaseRequest(BaseModel):
    """Request model for updating a knowledge base."""
    
    name: str | None = Field(
        None,
        min_length=1, 
        max_length=255, 
        description="New name for the knowledge base"
    )
    opening: str | None = Field(
        None,
        description="New opening line or introduction for the knowledge base"
    )
    prompt: str | None = Field(
        None,
        description="New custom prompt for the knowledge base"
    )
    
    @field_validator("name", mode="before")
    def validate_name(cls, v: str | None) -> str | None:
        """Validate the knowledge base name if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Name cannot be empty")
        return v