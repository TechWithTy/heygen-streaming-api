"""
Update knowledge base functionality for the HeyGen Streaming API.

This module provides functions for updating an existing knowledge base.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Path, status
from pydantic import BaseModel, Field

from ....client import client as heygen_client
from .._exceptions import (
    AuthenticationError,
    HeyGenAPIError,
    RateLimitError,
    ServerError,
)
from ._exceptions import (
    KnowledgeBaseError,
    KnowledgeBaseNotFoundError,
    KnowledgeBaseValidationError,
)
from ._responses import UpdateKnowledgeBaseResponse

router = APIRouter(tags=["knowledgebase"])
logger = logging.getLogger(__name__)

class UpdateKnowledgeBaseRequestModel(BaseModel):
    """Request model for updating a knowledge base."""
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="New name for the knowledge base"
    )
    opening: Optional[str] = Field(
        None,
        description="New opening line for the knowledge base"
    )
    prompt: Optional[str] = Field(
        None,
        description="New custom prompt for the knowledge base"
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "Updated Knowledge Base",
                "opening": "Updated opening line",
                "prompt": "Updated custom prompt"
            }
        }

@router.patch(
    "/knowledgebase/{knowledge_base_id}",
    response_model=UpdateKnowledgeBaseResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a knowledge base",
    responses={
        200: {"description": "Knowledge base updated successfully"},
        400: {"description": "Invalid request parameters"},
        401: {"description": "Invalid API key"},
        404: {"description": "Knowledge base not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Server error"},
    },
)
async def update_knowledge_base(
    request: UpdateKnowledgeBaseRequestModel,
    knowledge_base_id: str = Path(..., description="ID of the knowledge base to update"),
) -> UpdateKnowledgeBaseResponse:
    """
    Update an existing knowledge base with the specified parameters.

    Args:
        request: UpdateKnowledgeBaseRequestModel containing fields to update
        knowledge_base_id: ID of the knowledge base to update

    Returns:
        UpdateKnowledgeBaseResponse containing details of the updated knowledge base
    """
    # Convert Pydantic model to dict and remove None values
    update_data = request.dict(exclude_unset=True)
    
    # Ensure at least one field is being updated
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field (name, opening, or prompt) must be provided for update"
        )
    
    try:
        # Use the HeyGen client to update the knowledge base
        response = await heygen_client.update_knowledge_base(
            knowledge_base_id=knowledge_base_id,
            **update_data
        )
        
        return UpdateKnowledgeBaseResponse(**response)

    except KnowledgeBaseValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
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
        logger.error(f"API error in update_knowledge_base: {str(e)}")
        raise HTTPException(
            status_code=status_code,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Unexpected error in update_knowledge_base")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the knowledge base"
        )