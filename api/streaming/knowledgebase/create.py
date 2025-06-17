"""
Create knowledge base functionality for the HeyGen Streaming API.

This module provides functions for creating a new knowledge base with specified
name, opening line, and custom prompt.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ....client import client as heygen_client
from .._exceptions import (
    AuthenticationError,
    HeyGenAPIError,
    RateLimitError,
    ServerError,
)
from ._exceptions import KnowledgeBaseError, KnowledgeBaseValidationError
from ._requests import CreateKnowledgeBaseRequest
from ._responses import CreateKnowledgeBaseResponse

router = APIRouter(tags=["knowledgebase"])
logger = logging.getLogger(__name__)

class CreateKnowledgeBaseRequestModel(BaseModel):
    """Request model for creating a knowledge base."""
    name: str = Field(..., min_length=1, max_length=255, description="Name of the knowledge base")
    opening: str = Field(..., description="Opening line or introduction")
    prompt: str = Field(..., description="Custom prompt for the knowledge base")

@router.post(
    "/knowledgebase",
    response_model=CreateKnowledgeBaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new knowledge base",
    responses={
        201: {"description": "Knowledge base created successfully"},
        400: {"description": "Invalid request parameters"},
        401: {"description": "Invalid API key"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Server error"},
    },
)
async def create_knowledge_base(
    request: CreateKnowledgeBaseRequestModel,
) -> CreateKnowledgeBaseResponse:
    """
    Create a new knowledge base with the specified parameters.

    Args:
        request: CreateKnowledgeBaseRequestModel containing name, opening, and prompt

    Returns:
        CreateKnowledgeBaseResponse containing details of the created knowledge base
    """
    try:
        # Use the HeyGen client to create the knowledge base
        response = await heygen_client.create_knowledge_base(
            name=request.name,
            opening=request.opening,
            prompt=request.prompt
        )
        
        return CreateKnowledgeBaseResponse(**response)

    except KnowledgeBaseValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
        logger.error(f"API error in create_knowledge_base: {str(e)}")
        raise HTTPException(
            status_code=status_code,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Unexpected error in create_knowledge_base")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the knowledge base"
        )