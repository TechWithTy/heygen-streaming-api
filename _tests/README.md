# HeyGen Streaming SDK Test Suite

This directory contains the test suite for the HeyGen Streaming SDK.

## Test Structure

- `conftest.py`: Shared test fixtures and configuration
- `test_client.py`: Tests for the base HeyGenStreamingClient
- `test_knowledgebase.py`: Tests for Knowledge Base API endpoints
- `test_sessions.py`: Tests for Session management endpoints

## Running Tests

### Prerequisites

- Python 3.8+
- `pytest`
- `pytest-asyncio`
- `pytest-mock`
- `httpx`

### Installation

```bash
# Install test dependencies
pip install -e ".[test]"
```

### Running Tests

Run all tests:

```bash
pytest -v
```

Run a specific test file:

```bash
pytest -v tests/test_client.py
```

Run tests with coverage:

```bash
pytest --cov=heygen_streaming --cov-report=term-missing
```

## Test Fixtures

The test suite includes several useful fixtures:

- `heygen_client`: A pre-configured HeyGenStreamingClient instance
- `sample_knowledge_base_data`: Sample knowledge base data
- `sample_session_data`: Sample session data
- `mock_response`: Helper for creating mock HTTP responses

## Writing Tests

1. Use `pytest.mark.asyncio` for async test functions
2. Use `pytest.mark.parametrize` for parameterized tests
3. Use `mocker` fixture for mocking
4. Follow the Arrange-Act-Assert pattern

Example test:

```python
async def test_example(heygen_client, mocker):
    # Arrange
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"success": True}
    mocker.patch("httpx.AsyncClient.request", return_value=mock_response)
    
    # Act
    result = await heygen_client.some_method()
    
    # Assert
    assert result == {"success": True}
```

## Continuous Integration

Add this to your CI pipeline to run tests:

```yaml
steps:
  - name: Run tests
    run: |
      pip install -e ".[test]"
      pytest -v --cov=heygen_streaming --cov-report=xml
    env:
      HEYGEN_API_KEY: ${{ secrets.HEYGEN_API_KEY }}
```

## Debugging

To debug tests, use `pdb`:

```python
import pdb; pdb.set_trace()
```

Or run with `--pdb` to drop into debugger on failure:

```bash
pytest --pdb
```

## Best Practices

1. Keep tests focused and test one thing per test function
2. Use descriptive test names
3. Mock external dependencies
4. Test both success and error cases
5. Keep tests fast and independent
6. Use fixtures to reduce code duplication
