"""Pytest configuration and fixtures for HeyGen Streaming SDK tests."""
from __future__ import annotations

import asyncio
import sys
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio
from httpx import AsyncClient, Response

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from heygen_streaming.client import HeyGenStreamingClient

# Constants
TEST_API_KEY = "test_api_key_123"
TEST_BASE_URL = "https://api.heygen.com/v1"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def mock_httpx_client() -> AsyncGenerator[AsyncClient, None]:
    """Create a mock HTTPX client for testing."""
    async with AsyncClient() as client:
        yield client


@pytest.fixture
def sample_knowledge_base_data() -> dict[str, Any]:
    """Return sample knowledge base data for testing."""
    return {
        "id": "kb_123",
        "name": "Test Knowledge Base",
        "opening": "Hello, how can I help you today?",
        "prompt": "You are a helpful assistant.",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_session_data() -> dict[str, Any]:
    """Return sample session data for testing."""
    return {
        "session_id": "sess_123",
        "token": "test_token_123",
        "expires_at": "2023-12-31T23:59:59Z",
        "status": "active",
    }


@pytest.fixture
def mock_response():
    """Create a mock HTTP response."""
    def _create_mock_response(
        status_code: int = 200,
        json_data: dict | None = None,
        text: str = "",
        headers: dict | None = None,
    ) -> Response:
        response = Response(
            status_code=status_code,
            json=json_data if json_data is not None else {},
            text=text,
            request=None,  # type: ignore
        )
        if headers:
            response.headers.update(headers)
        return response

    return _create_mock_response


@pytest_asyncio.fixture
async def heygen_client() -> AsyncGenerator[HeyGenStreamingClient, None]:
    """Create a HeyGen client for testing."""
    client = HeyGenStreamingClient(api_key=TEST_API_KEY, base_url=TEST_BASE_URL)
    await client.start()
    yield client
    await client.close()
