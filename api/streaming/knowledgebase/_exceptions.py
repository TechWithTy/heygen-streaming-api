"""
Exceptions for the HeyGen Knowledge Base API.

This module contains custom exceptions specific to the knowledge base operations.
"""

from .._exceptions import HeyGenAPIError


class KnowledgeBaseError(HeyGenAPIError):
    """Base exception for knowledge base related errors."""
    pass

class KnowledgeBaseNotFoundError(KnowledgeBaseError):
    """Raised when a knowledge base is not found."""
    def __init__(self, message: str = "Knowledge base not found"):
        super().__init__(message=message, status_code=404)

class DocumentError(KnowledgeBaseError):
    """Base exception for document related errors."""
    pass

class DocumentNotFoundError(DocumentError):
    """Raised when a document is not found in a knowledge base."""
    def __init__(self, message: str = "Document not found in knowledge base"):
        super().__init__(message=message, status_code=404)
        
class KnowledgeBaseValidationError(KnowledgeBaseError):
    """Raised when knowledge base validation fails."""
    def __init__(self, message: str = "Invalid knowledge base parameters", status_code: int = 400):
        super().__init__(message=message, status_code=status_code)