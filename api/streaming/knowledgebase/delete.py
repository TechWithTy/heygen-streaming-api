"""
Delete knowledge base functionality for the HeyGen Streaming API.

This module provides functions for deleting an existing knowledge base.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Path, status
from pydantic import BaseModel, Field

from ....client import client as heygen_client
from .._exceptions import (
    AuthenticationError,
    HeyGenAPIError,
    RateLimitError,
    ServerError,
)
from ._exceptions import KnowledgeBaseError, KnowledgeBaseNotFoundError
from ._responses import DeleteKnowledgeBaseResponse

router = APIRouter(tags=["knowledgebase"])
logger = logging.getLogger(__name__)

class DeleteKnowledgeBaseResponseModel(BaseModel):
    """Response model for deleting a knowledge base."""
    success: bool = Field(..., description="Whether the deletion was successful")
    knowledge_base_id: str = Field(..., description="ID of the deleted knowledge base")
    message: str = Field(..., description="Status message")

@router.delete(
    "/knowledgebase/{knowledge_base_id}",
    response_model=DeleteKnowledgeBaseResponseModel,
    status_code=status.HTTP_200_OK,
    summary="Delete a knowledge base",
    responses={
        200: {"description": "Knowledge base deleted successfully"},
        400: {"description": "Invalid knowledge base ID"},
        401: {"description": "Invalid API key"},
        404: {"description": "Knowledge base not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Server error"},
    },
)
async def delete_knowledge_base(
    knowledge_base_id: str = Path(..., description="ID of the knowledge base to delete"),
) -> DeleteKnowledgeBaseResponseModel:
    """
    Delete a knowledge base by its ID.

    Args:
        knowledge_base_id: ID of the knowledge base to delete

    Returns:
        DeleteKnowledgeBaseResponseModel containing deletion status
    """
    if not knowledge_base_id or not knowledge_base_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="knowledge_base_id cannot be empty"
        )

    try:
        # Use the HeyGen client to delete the knowledge base
        await heygen_client.delete_knowledge_base(knowledge_base_id=knowledge_base_id)
        
        return DeleteKnowledgeBaseResponseModel(
            success=True,
            knowledge_base_id=knowledge_base_id,
            message="Knowledge base deleted successfully"
        )

    except KnowledgeBaseNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except RateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except (ServerError, HeyGenAPIError, KnowledgeBaseError) as e:
        status_code = getattr(e, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.error(f"API error in delete_knowledge_base: {str(e)}")
        raise HTTPException(
            status_code=status_code,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Unexpected error in delete_knowledge_base")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the knowledge base"
        )