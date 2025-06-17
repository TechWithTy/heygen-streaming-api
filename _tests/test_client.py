"""Tests for the HeyGen Streaming API client."""
from __future__ import annotations

from typing import Any, TypeVar
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from heygen_streaming.api.streaming._exceptions import (
    AuthenticationError,
    HeyGenAPIError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from heygen_streaming.client import HeyGenStreamingClient

T = TypeVar('T')
Response = dict[str, Any]  # Type alias for response data

# Test constants
TEST_API_KEY = "test_api_key_123"
TEST_BASE_URL = "https://api.test.heygen.com/v1"
TEST_ENDPOINT = "/test/endpoint"
TEST_RESPONSE = {"status": "success", "data": {"id": "123"}}
TEST_HEADERS = {"Authorization": f"Bearer {TEST_API_KEY}", "Content-Type": "application/json"}


class TestHeyGenStreamingClient:
    """Test suite for HeyGenStreamingClient."""

    @pytest.fixture
    def mock_client(self):
        with patch("httpx.AsyncClient") as mock_async_client:
            mock_client = AsyncMock()
            mock_async_client.return_value.__aenter__.return_value = mock_client
            yield mock_client
    
    @pytest.fixture
    def client(self):
        return HeyGenStreamingClient(api_key=TEST_API_KEY, base_url=TEST_BASE_URL)

    async def test_client_initialization_defaults(self):
        """Test client initialization with default parameters."""
        client = HeyGenStreamingClient(api_key=TEST_API_KEY)
        assert client._api_key == TEST_API_KEY
        assert client._base_url == "https://api.heygen.com/v1"
        assert client._timeout == 30.0
        assert client._max_retries == 3

    async def test_client_initialization_custom_params(self):
        """Test client initialization with custom parameters."""
        client = HeyGenStreamingClient(
            api_key=TEST_API_KEY,
            base_url=TEST_BASE_URL,
            timeout=60.0,
            max_retries=5,
        )
        assert client._api_key == TEST_API_KEY
        assert client._base_url == TEST_BASE_URL
        assert client._timeout == 60.0
        assert client._max_retries == 5

    async def test_successful_request(self, client, mock_client):
        """Test successful request handling."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = TEST_RESPONSE
        mock_client.request.return_value = mock_response

        # Make request
        response = await client._request("GET", TEST_ENDPOINT, dict)

        # Assertions
        assert response == TEST_RESPONSE
        mock_client.request.assert_called_once_with(
            "GET",
            f"{TEST_BASE_URL}{TEST_ENDPOINT}",
            headers=TEST_HEADERS,
            json=None,
            timeout=30.0,
        )

    @pytest.mark.parametrize(
        "status_code,exception_cls",
        [
            (401, AuthenticationError),
            (403, AuthenticationError),
            (429, RateLimitError),
            (500, ServerError),
            (502, ServerError),
        ],
    )
    async def test_request_error_handling(self, client, mock_client, status_code, exception_cls):
        """Test error handling for different HTTP status codes."""
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.text = "Error message"
        mock_response.json.return_value = {"error": {"message": "Error message"}}
        mock_client.request.return_value = mock_response

        # Assert exception is raised
        with pytest.raises(exception_cls) as exc_info:
            await client._request("GET", TEST_ENDPOINT, dict)

        assert "Error message" in str(exc_info.value)

    async def test_request_validation_error(self, client, mock_client):
        """Test validation error handling."""
        # Mock response with invalid data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "data"}
        mock_client.request.return_value = mock_response

        # Assert validation error is raised
        with pytest.raises(ValidationError):
            await client._request("GET", TEST_ENDPOINT, dict)

    async def test_close(self, client, mock_client):
        """Test client close method."""
        await client.close()
        mock_client.aclose.assert_called_once()

    async def test_retry_logic(self, client, mock_client):
        """Test request retry logic."""
        # Mock first request to fail with 502, then succeed
        error_response = MagicMock()
        error_response.status_code = 502
        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = TEST_RESPONSE

        mock_client.request.side_effect = [error_response, success_response]

        # Make request
        response = await client._request("GET", TEST_ENDPOINT, dict)

        # Assertions
        assert response == TEST_RESPONSE
        assert mock_client.request.call_count == 2

    async def test_start_and_close(self):
        """Test starting and closing the client."""
        client = HeyGenStreamingClient(api_key=TEST_API_KEY)
        await client.start()
        assert client._client is not None
        await client.close()
        assert client._client is None

    async def test_context_manager(self):
        """Test client usage as a context manager."""
        async with HeyGenStreamingClient(api_key=TEST_API_KEY) as client:
            assert isinstance(client, HeyGenStreamingClient)
            assert client._client is not None
        assert client._client is None

    @pytest.mark.parametrize(
        "status_code,exception_cls",
        [
            (401, AuthenticationError),
            (429, RateLimitError),
            (500, ServerError),
            (400, HeyGenAPIError),
        ],
    )
    async def test_handle_error_responses(
        self, status_code: int, exception_cls: type[Exception], mocker
    ):
        """Test error response handling."""
        client = HeyGenStreamingClient(api_key="test_key")
        
        # Mock the _request method to return an error response
        mock_response = Response(
            status_code=status_code,
            json={"message": f"Error {status_code}"},
            request=None,  # type: ignore
        )
        
        mocker.patch(
            "httpx.AsyncClient.request",
            return_value=mock_response,
        )
        
        with pytest.raises(exception_cls):
            await client._request("GET", "/test", dict)  # type: ignore

    async def test_create_session_token(self, heygen_client, sample_session_data, mocker):
        """Test creating a session token."""
        mock_response = mocker.Mock()
        mock_response.json.return_value = sample_session_data
        mocker.patch(
            "httpx.AsyncClient.request",
            return_value=mock_response,
        )
        
        result = await heygen_client.create_session_token(
            session_id="test_session",
            expires_in=3600,
        )
        
        assert result == sample_session_data
        
    async def test_list_knowledge_bases(self, heygen_client, sample_knowledge_base_data, mocker):
        """Test listing knowledge bases."""
        mock_response = mocker.Mock()
        mock_response.json.return_value = {"data": [sample_knowledge_base_data]}
        mocker.patch(
            "httpx.AsyncClient.request",
            return_value=mock_response,
        )
        
        result = await heygen_client.list_knowledge_bases()
        
        assert "data" in result
        assert len(result["data"]) == 1
        assert result["data"][0]["id"] == sample_knowledge_base_data["id"]
