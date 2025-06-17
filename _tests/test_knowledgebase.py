"""Tests for the HeyGen Streaming API knowledge base endpoints."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from heygen_streaming.api.streaming.knowledgebase._enums import (
    DocumentStatus,
    KnowledgeBaseStatus,
)
from heygen_streaming.api.streaming.knowledgebase._exceptions import (
    DocumentError,
    KnowledgeBaseNotFoundError,
    KnowledgeBaseValidationError,
)
from heygen_streaming.api.streaming.knowledgebase._responses import (
    CreateKnowledgeBaseResponse,
    DeleteKnowledgeBaseResponse,
    KnowledgeBaseInfo,
    ListKnowledgeBasesResponse,
    UpdateKnowledgeBaseResponse,
)
from heygen_streaming.client import HeyGenStreamingClient

# Test constants
TEST_KB_ID = "test_kb_123"
TEST_DOCUMENT_ID = "doc_123"
TEST_KB_NAME = "Test Knowledge Base"
TEST_KB_OPENING = "Hello! How can I help you today?"
TEST_KB_PROMPT = "You are a helpful assistant for testing purposes."

# Fixtures


@pytest.fixture
def sample_document_info() -> dict[str, Any]:
    """Return sample document info for testing."""
    now = int(datetime.now(timezone.utc).timestamp())
    return {
        "document_id": TEST_DOCUMENT_ID,
        "name": "test_document.pdf",
        "status": DocumentStatus.PROCESSED,
        "created_at": now,
        "processed_at": now,
        "error": None,
    }


@pytest.fixture
def sample_knowledge_base_info(sample_document_info: dict[str, Any]) -> dict[str, Any]:
    """Return sample knowledge base info for testing."""
    now = int(datetime.now(timezone.utc).timestamp())
    return {
        "knowledge_base_id": TEST_KB_ID,
        "name": TEST_KB_NAME,
        "description": "Test knowledge base description",
        "status": KnowledgeBaseStatus.ACTIVE,
        "created_at": now,
        "updated_at": now,
        "document_count": 1,
        "documents": [sample_document_info],
    }


class TestKnowledgeBaseAPI:
    """Test suite for Knowledge Base API endpoints."""

    async def test_create_knowledge_base_success(self, mocker):
        """Test creating a knowledge base successfully."""
        # Setup
        client = HeyGenStreamingClient()
        response_data = CreateKnowledgeBaseResponse(
            knowledge_base_id=TEST_KB_ID,
            name=TEST_KB_NAME,
            status=KnowledgeBaseStatus.ACTIVE,
            created_at=int(datetime.now(timezone.utc).timestamp()),
        )

        mocker.patch.object(
            client, "_request",
            return_value=response_data.model_dump()
        )

        # Test
        result = await client.create_knowledge_base(
            name=TEST_KB_NAME,
            opening=TEST_KB_OPENING,
            prompt=TEST_KB_PROMPT,
        )

        # Assert
        assert isinstance(result, CreateKnowledgeBaseResponse)
        assert result.knowledge_base_id == TEST_KB_ID
        assert result.name == TEST_KB_NAME
        assert result.status == KnowledgeBaseStatus.ACTIVE

    async def test_list_knowledge_bases_success(self, mocker, sample_knowledge_base_info):
        """Test listing knowledge bases successfully."""
        # Setup
        client = HeyGenStreamingClient()
        kb_info = KnowledgeBaseInfo(**sample_knowledge_base_info)
        response_data = ListKnowledgeBasesResponse(
            knowledge_bases=[kb_info],
            total=1,
            page=1,
            page_size=10,
        )

        mocker.patch.object(
            client, "_request",
            return_value=response_data.model_dump()
        )

        # Test
        result = await client.list_knowledge_bases()

        # Assert
        assert isinstance(result, ListKnowledgeBasesResponse)
        assert len(result.knowledge_bases) == 1
        assert result.knowledge_bases[0].knowledge_base_id == TEST_KB_ID
        assert result.total == 1

    async def test_update_knowledge_base_success(self, mocker):
        """Test updating a knowledge base successfully."""
        # Setup
        client = HeyGenStreamingClient()
        updated_name = "Updated Test KB"
        updated_opening = "Updated opening"

        response_data = UpdateKnowledgeBaseResponse(
            knowledge_base_id=TEST_KB_ID,
            name=updated_name,
            status=KnowledgeBaseStatus.ACTIVE,
            updated_at=int(datetime.now(timezone.utc).timestamp()),
        )

        mocker.patch.object(
            client, "_request",
            return_value=response_data.model_dump()
        )

        # Test
        result = await client.update_knowledge_base(
            knowledge_base_id=TEST_KB_ID,
            name=updated_name,
            opening=updated_opening,
        )

        # Assert
        assert isinstance(result, UpdateKnowledgeBaseResponse)
        assert result.knowledge_base_id == TEST_KB_ID
        assert result.name == updated_name
        assert result.status == KnowledgeBaseStatus.ACTIVE

    async def test_delete_knowledge_base_success(self, mocker):
        """Test deleting a knowledge base successfully."""
        # Setup
        client = HeyGenStreamingClient()
        response_data = DeleteKnowledgeBaseResponse(
            success=True,
            knowledge_base_id=TEST_KB_ID,
            message="Knowledge base deleted successfully",
        )

        mocker.patch.object(
            client, "_request",
            return_value=response_data.model_dump()
        )

        # Test
        result = await client.delete_knowledge_base(knowledge_base_id=TEST_KB_ID)

        # Assert
        assert isinstance(result, DeleteKnowledgeBaseResponse)
        assert result.success is True
        assert result.knowledge_base_id == TEST_KB_ID

    @pytest.mark.parametrize(
        "exception_cls,status_code,error_message",
        [
            (KnowledgeBaseNotFoundError, 404, "Knowledge base not found"),
            (KnowledgeBaseValidationError, 400, "Invalid request data"),
            (DocumentError, 500, "Internal server error"),
        ],
    )
    async def test_knowledge_base_error_handling(
        self, mocker, exception_cls, status_code, error_message
    ):
        """Test error handling for knowledge base operations."""
        # Setup
        client = HeyGenStreamingClient()

        # Mock the _request method to raise the appropriate exception
        async def mock_request(*_args, **_kwargs):
            raise exception_cls(message=error_message, status_code=status_code)

        mocker.patch.object(client, "_request", side_effect=mock_request)

        # Test & Assert
        with pytest.raises(exception_cls) as exc_info:
            if exception_cls == KnowledgeBaseNotFoundError:
                await client.get_knowledge_base(knowledge_base_id="nonexistent")
            elif exception_cls == KnowledgeBaseValidationError:
                await client.create_knowledge_base(name="", opening="", prompt="")
            else:
                await client.list_knowledge_bases()
        assert error_message in str(exc_info.value)
        assert exc_info.value.status_code == status_code
