"""
List knowledge bases functionality for the HeyGen Streaming API.

This module provides functions for retrieving a list of all knowledge bases
associated with the authenticated account.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from ....client import client as heygen_client
from .._exceptions import (
    AuthenticationError,
    HeyGenAPIError,
    RateLimitError,
    ServerError,
)
from ._exceptions import KnowledgeBaseError
from ._responses import ListKnowledgeBasesResponse

router = APIRouter(tags=["knowledgebase"])
logger = logging.getLogger(__name__)

class ListKnowledgeBasesQueryParams(BaseModel):
    """Query parameters for listing knowledge bases."""
    limit: Optional[int] = Field(
        None,
        ge=1,
        le=100,
        description="Maximum number of items to return per page"
    )
    offset: Optional[int] = Field(
        None,
        ge=0,
        description="Number of items to skip before starting to collect the result set"
    )

@router.get(
    "/knowledgebase",
    response_model=ListKnowledgeBasesResponse,
    status_code=status.HTTP_200_OK,
    summary="List all knowledge bases",
    responses={
        200: {"description": "List of knowledge bases retrieved successfully"},
        401: {"description": "Invalid API key"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Server error"},
    },
)
async def list_knowledge_bases(
    limit: Optional[int] = Query(
        None,
        ge=1,
        le=100,
        description="Maximum number of items to return per page"
    ),
    offset: Optional[int] = Query(
        None,
        ge=0,
        description="Number of items to skip before starting to collect the result set"
    ),
) -> ListKnowledgeBasesResponse:
    """
    Retrieve a paginated list of all knowledge bases associated with the authenticated account.

    Args:
        limit: Maximum number of items to return per page (1-100)
        offset: Number of items to skip

    Returns:
        ListKnowledgeBasesResponse containing the paginated list of knowledge bases
    """
    try:
        # Use the HeyGen client to list knowledge bases
        response = await heygen_client.list_knowledge_bases(
            limit=limit,
            offset=offset
        )
        
        return ListKnowledgeBasesResponse(**response)

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
        logger.error(f"API error in list_knowledge_bases: {str(e)}")
        raise HTTPException(
            status_code=status_code,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Unexpected error in list_knowledge_bases")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while listing knowledge bases"
        )
