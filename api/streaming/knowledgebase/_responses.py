"""
Response models for the HeyGen Knowledge Base API.

This module contains all the response models used in the knowledge base API.
"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from ._enums import DocumentStatus, KnowledgeBaseStatus


class DocumentInfo(BaseModel):
    """Model representing a document in a knowledge base."""
    
    document_id: str = Field(..., description="Unique identifier for the document")
    name: str = Field(..., description="Name of the document")
    status: DocumentStatus = Field(..., description="Current status of the document")
    created_at: int = Field(..., description="Timestamp when the document was created")
    processed_at: int | None = Field(None, description="Timestamp when processing completed")
    error: str | None = Field(None, description="Error message if processing failed")

    @property
    def created_at_dt(self) -> datetime:
        """Return created_at as a datetime object."""
        return datetime.fromtimestamp(self.created_at)

    @property
    def processed_at_dt(self) -> datetime | None:
        """Return processed_at as a datetime object if available."""
        return datetime.fromtimestamp(self.processed_at) if self.processed_at else None

class KnowledgeBaseInfo(BaseModel):
    """Model representing a knowledge base."""
    
    knowledge_base_id: str = Field(..., description="Unique identifier for the knowledge base")
    name: str = Field(..., description="Name of the knowledge base")
    description: str | None = Field(None, description="Description of the knowledge base")
    status: KnowledgeBaseStatus = Field(..., description="Current status of the knowledge base")
    created_at: int = Field(..., description="Timestamp when the knowledge base was created")
    updated_at: int = Field(..., description="Timestamp when the knowledge base was last updated")
    document_count: int = Field(..., description="Number of documents in the knowledge base")
    documents: list[DocumentInfo] | None = Field(
        None, 
        description="List of documents in the knowledge base (if expanded)"
    )

    @property
    def created_at_dt(self) -> datetime:
        """Return created_at as a datetime object."""
        return datetime.fromtimestamp(self.created_at)

    @property
    def updated_at_dt(self) -> datetime:
        """Return updated_at as a datetime object."""
        return datetime.fromtimestamp(self.updated_at)

class ListKnowledgeBasesResponse(BaseModel):
    """Response model for listing knowledge bases."""
    
    knowledge_bases: list[KnowledgeBaseInfo] = Field(
        default_factory=list,
        description="List of knowledge bases"
    )
    total: int = Field(..., description="Total number of knowledge bases")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(10, description="Number of items per page")

    @field_validator("page", "page_size", "total")
    def validate_positive_integers(cls, v: int) -> int:
        """Validate that page, page_size, and total are positive integers."""
        if v < 0:
            raise ValueError("Value must be a non-negative integer")
        return v
    
class CreateKnowledgeBaseResponse(BaseModel):
    """Response model for creating a knowledge base."""
    
    knowledge_base_id: str = Field(..., description="ID of the created knowledge base")
    name: str = Field(..., description="Name of the knowledge base")
    status: KnowledgeBaseStatus = Field(..., description="Initial status of the knowledge base")
    created_at: int = Field(..., description="Timestamp when the knowledge base was created")
    
    @property
    def created_at_dt(self) -> datetime:
        """Return created_at as a datetime object."""
        return datetime.fromtimestamp(self.created_at)

class UpdateKnowledgeBaseResponse(BaseModel):
    """Response model for updating a knowledge base."""
    
    knowledge_base_id: str = Field(..., description="ID of the updated knowledge base")
    name: str = Field(..., description="Updated name of the knowledge base")
    status: KnowledgeBaseStatus = Field(..., description="Current status of the knowledge base")
    updated_at: int = Field(..., description="Timestamp when the knowledge base was last updated")
    
    @property
    def updated_at_dt(self) -> datetime:
        """Return updated_at as a datetime object."""
        return datetime.fromtimestamp(self.updated_at)
    
class DeleteKnowledgeBaseResponse(BaseModel):
    """Response model for deleting a knowledge base."""
    
    success: bool = Field(..., description="Whether the deletion was successful")
    knowledge_base_id: str = Field(..., description="ID of the deleted knowledge base")
    message: str = Field(..., description="Deletion status message")