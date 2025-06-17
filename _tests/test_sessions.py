"""Tests for the HeyGen Streaming API session endpoints."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

import pytest
from httpx import Response

from heygen_streaming.api.streaming._exceptions import (
    AuthenticationError,
    HeyGenAPIError,
    HeyGenValidationError,
    RateLimitError,
    ServerError,
    SessionNotFoundError,
)
from heygen_streaming.client import HeyGenStreamingClient
from heygen_streaming.api.streaming.new_sessions import NewSessionRequest, NewSessionResponse
from heygen_streaming.api.streaming.start_session import StartSessionResponse
from heygen_streaming.api.streaming.send_task import SendTaskRequest, TaskResponse

# Test data
TEST_SESSION_ID = "test_session_123"
TEST_AVATAR_ID = "avatar_123"
TEST_TASK_ID = "task_123"

class TestSessionAPI:
    """Test suite for Session management endpoints."""

    async def test_create_session(self, mocker):
        """Test creating a new streaming session."""
        # Setup
        client = HeyGenStreamingClient()
        mock_response = {
            "session_id": TEST_SESSION_ID,
            "status": "created",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        
        mocker.patch.object(
            client, "_request", 
            return_value=NewSessionResponse.model_validate(mock_response)
        )
        
        # Test
        request = NewSessionRequest(
            session_id=TEST_SESSION_ID,
            avatar_id=TEST_AVATAR_ID,
            voice_id="voice_123",
            text="Hello, world!",
        )
        
        result = await client.create_session(request)
        
        # Assert
        assert isinstance(result, NewSessionResponse)
        assert result.session_id == TEST_SESSION_ID
        assert result.status == "created"
        client._request.assert_called_once()
        
    async def test_start_session_success(self, mocker):
        """Test starting a session successfully."""
        # Setup
        client = HeyGenStreamingClient()
        mock_response = {
            "session_id": TEST_SESSION_ID,
            "status": "started",
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        
        mocker.patch.object(
            client, "_request",
            return_value=StartSessionResponse.model_validate(mock_response)
        )
        
        # Test
        result = await client.start_session(TEST_SESSION_ID)
        
        # Assert
        assert isinstance(result, StartSessionResponse)
        assert result.session_id == TEST_SESSION_ID
        assert result.status == "started"
        
    async def test_send_task_success(self, mocker):
        """Test sending a task to a session."""
        # Setup
        client = HeyGenStreamingClient()
        mock_response = {
            "task_id": TEST_TASK_ID,
            "status": "queued",
            "duration_ms": 1234,
        }
        
        mocker.patch.object(
            client, "_request",
            return_value=TaskResponse.model_validate(mock_response)
        )
        
        # Test
        request = SendTaskRequest(
            session_id=TEST_SESSION_ID,
            text="Hello, this is a test task.",
        )
        
        result = await client.send_task(request)
        
        # Assert
        assert isinstance(result, TaskResponse)
        assert result.task_id == TEST_TASK_ID
        assert result.status == "queued"
        
    async def test_session_not_found_error(self, mocker):
        """Test handling of session not found error."""
        # Setup
        client = HeyGenStreamingClient()
        mocker.patch.object(
            client, "_request",
            side_effect=SessionNotFoundError("Session not found")
        )
        
        # Test & Assert
        with pytest.raises(SessionNotFoundError):
            await client.start_session("nonexistent_session")
            
    async def test_authentication_error(self, mocker):
        """Test handling of authentication errors."""
        # Setup
        client = HeyGenStreamingClient()
        mocker.patch.object(
            client, "_request",
            side_effect=AuthenticationError("Invalid API key")
        )
        
        # Test & Assert
        with pytest.raises(AuthenticationError):
            await client.start_session(TEST_SESSION_ID)
            
    async def test_rate_limit_error(self, mocker):
        """Test handling of rate limit errors."""
        # Setup
        client = HeyGenStreamingClient()
        mocker.patch.object(
            client, "_request",
            side_effect=RateLimitError("Rate limit exceeded")
        )
        
        # Test & Assert
        with pytest.raises(RateLimitError):
            await client.start_session(TEST_SESSION_ID)
            
    async def test_validation_error(self, mocker):
        """Test handling of validation errors."""
        # Setup
        client = HeyGenStreamingClient()
        mocker.patch.object(
            client, "_request",
            side_effect=HeyGenValidationError("Invalid request data")
        )
        
        # Test & Assert
        with pytest.raises(HeyGenValidationError):
            await client.start_session("")  # Empty session ID should be invalid
            
    async def test_server_error(self, mocker):
        """Test handling of server errors."""
        # Setup
        client = HeyGenStreamingClient()
        mocker.patch.object(
            client, "_request",
            side_effect=ServerError("Internal server error")
        )
        
        # Test & Assert
        with pytest.raises(ServerError):
            await client.start_session(TEST_SESSION_ID)
            
    async def test_generic_api_error(self, mocker):
        """Test handling of generic API errors."""
        # Setup
        client = HeyGenStreamingClient()
        mocker.patch.object(
            client, "_request",
            side_effect=HeyGenAPIError("Generic API error")
        )
        
        # Test & Assert
        with pytest.raises(HeyGenAPIError):
            await client.start_session(TEST_SESSION_ID)

    async def test_keep_alive(self, mocker):
        """Test keeping a session alive."""
        # Setup
        client = HeyGenStreamingClient()
        mock_response = {
            "session_id": TEST_SESSION_ID,
            "status": "active",
            "expires_at": (datetime.now(timezone.utc).timestamp() + 300) * 1000  # 5 minutes from now
        }
        
        mocker.patch.object(
            client, "_request",
            return_value=StartSessionResponse.model_validate(mock_response)
        )

        # Test
        result = await client.keep_alive(TEST_SESSION_ID)

        # Assert
        assert isinstance(result, StartSessionResponse)
        assert result.session_id == TEST_SESSION_ID
        assert result.status == "active"

    async def test_list_avatars(self, mocker):
        """Test listing available avatars."""
        # Setup
        client = HeyGenStreamingClient()
        avatar_data = {
            "data": [
                {"id": "avatar1", "name": "Avatar 1", "status": "ready"},
                {"id": "avatar2", "name": "Avatar 2", "status": "ready"},
            ]
        }
        
        mocker.patch.object(
            client, "_request",
            return_value=avatar_data
        )

        # Test
        result = await client.list_avatars()

        # Assert
        assert "data" in result
        assert len(result["data"]) == 2
        assert result["data"][0]["id"] == "avatar1"
