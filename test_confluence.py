import pytest
import os
from unittest.mock import patch, AsyncMock, Mock

# Import functions to be tested from confluence.py
# Assuming confluence.py is in the same directory or accessible via PYTHONPATH
from confluence import list_spaces, search_content, list_pages_in_space, make_confluence_request, mcp

# Basic configuration for tests (can be overridden by environment variables)
TEST_CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL", "http://fake-confluence-url.com/rest/api")
TEST_USERNAME = os.getenv("USERNAME", "testuser")
TEST_API_TOKEN = os.getenv("API_TOKEN", "testtoken")

@pytest.fixture(autouse=True)
def setup_env_vars(monkeypatch):
    monkeypatch.setenv("CONFLUENCE_BASE_URL", TEST_CONFLUENCE_BASE_URL)
    monkeypatch.setenv("USERNAME", TEST_USERNAME)
    monkeypatch.setenv("API_TOKEN", TEST_API_TOKEN)
    # Ensure PORT is set for mcp initialization if it reads it at import time
    monkeypatch.setenv("PORT", "8888")


@pytest.mark.asyncio
async def test_list_spaces_pagination():
    '''Test that list_spaces includes start and limit parameters.'''
    # Patch make_confluence_request directly for this test
    with patch('confluence.make_confluence_request', new_callable=AsyncMock) as mock_make_request:
        # Set the return value for make_confluence_request
        mock_make_request.return_value = {"results": [], "start": 5, "limit": 10, "size": 0}

        await list_spaces(limit=10, start=5)

        # Check that make_confluence_request was called with correct params
        mock_make_request.assert_called_once()
        called_args = mock_make_request.call_args[1] # Get keyword arguments

        assert called_args.get('params').get("limit") == 10
        assert called_args.get('params').get("start") == 5
        assert f"{TEST_CONFLUENCE_BASE_URL}/space" == mock_make_request.call_args[0][0] # Check URL

@pytest.mark.asyncio
async def test_list_spaces_name_filter():
    '''Test that list_spaces uses 'name' for query parameter.'''
    with patch('confluence.make_confluence_request', new_callable=AsyncMock) as mock_make_request:
        mock_make_request.return_value = {"results": [], "start": 0, "limit": 25, "size": 0}
        
        await list_spaces(query="MySpace")

        mock_make_request.assert_called_once()
        called_params = mock_make_request.call_args[1].get('params')
        
        assert called_params is not None
        assert called_params.get("name") == "MySpace"
        assert "spaceKey" not in called_params

@pytest.mark.asyncio
async def test_search_content_pagination():
    '''Test that search_content includes start and limit parameters.'''
    with patch('confluence.make_confluence_request', new_callable=AsyncMock) as mock_make_request:
        mock_make_request.return_value = {"results": [], "start": 10, "limit": 20, "size": 0}

        await search_content(query="test query", limit=20, start=10)

        mock_make_request.assert_called_once()
        called_params = mock_make_request.call_args[1].get('params')

        assert called_params is not None
        assert called_params.get("limit") == 20
        assert called_params.get("start") == 10
        assert 'text ~ "test query"' in called_params.get("cql", "")

@pytest.mark.asyncio
async def test_make_confluence_request_error_handling():
    '''Test that make_confluence_request returns a dict with 'error' key on HTTPError.'''
    # Patch make_confluence_request itself for this test
    with patch('confluence.make_confluence_request', new_callable=AsyncMock) as mock_make_request_direct:
        # Define the expected error dictionary
        error_dict = {"error": "Simulated error from make_confluence_request mock"}
        mock_make_request_direct.return_value = error_dict
        
        # Call the function (which is now the mock)
        result = await make_confluence_request(url="http://fake/api")
        
        assert isinstance(result, dict)
        assert "error" in result
        assert "Error making request" in result["error"]

# It might be necessary to add pytest-asyncio to requirements.txt
# The worker should also ensure httpx is available for the side_effect.
# These tests use unittest.mock and pytest.
# If these are not in requirements.txt, they might need to be added or the tests adjusted.
