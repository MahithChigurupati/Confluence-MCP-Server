from typing import Any, Optional
from mcp.server.fastmcp import FastMCP
import httpx
import sys
from urllib.parse import quote
import base64
import os
from dotenv import load_dotenv
import signal

# Load environment variables from .env file
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("confluence")

# Constants
try:
    port_str = os.getenv("PORT")
    if port_str is None:
        print("PORT environment variable not set, defaulting to 8000.", file=sys.stderr)
        mcp.settings.port = 8000
    else:
        mcp.settings.port = int(port_str)
except ValueError:
    print(f"Invalid PORT value: {port_str}. Defaulting to 8000.", file=sys.stderr)
    mcp.settings.port = 8000
CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
USERNAME = os.getenv("USERNAME")
API_TOKEN = os.getenv("API_TOKEN")

# Ensure required environment variables are set
if not CONFLUENCE_BASE_URL or not USERNAME or not API_TOKEN:
    raise ValueError("Missing required environment variables. Please check your .env file.")

# Define a signal handler function
def signal_handler(sig, frame):
    print('Shutting down server...')
    sys.exit(0)

# Register the signal handler for SIGINT
signal.signal(signal.SIGINT, signal_handler)

async def make_confluence_request(url: str, method: str = "GET", params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """Make a request to the Confluence API with proper error handling."""
    if not USERNAME or not API_TOKEN:
        return {"error": "Please set your Confluence username and API token"}

    # Create basic auth header
    auth_string = f"{USERNAME}:{API_TOKEN}"
    auth_bytes = auth_string.encode('ascii')
    base64_auth = base64.b64encode(auth_bytes).decode('ascii')

    headers = {
        "Authorization": f"Basic {base64_auth}",
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
            else:
                response = await client.request(method, url, headers=headers, json=params, timeout=30.0)
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": f"Error making request: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
async def list_spaces(
    query: Optional[str] = None,
    limit: Optional[int] = 25,
    start: Optional[int] = 0
) -> str:
    """List available Confluence spaces with optional filtering.
    
    Args:
        query: Optional search text to filter spaces by name/description
        limit: Maximum number of spaces to return (default: 25)
        start: Index of the first result to return (for pagination)
    """
    url = f"{CONFLUENCE_BASE_URL}/space"
    params = {
        "limit": limit,
        "start": start,
        "expand": "description.plain,homepage"
    }
    if query:
        params["name"] = query

    data = await make_confluence_request(url, params=params)
    if "error" in data:
        return data

    # Format the response
    result = []
    for space in data.get("results", []):
        space_info = f"""
            Space: {space.get('name', 'Unknown')}
            Key: {space.get('key', 'Unknown')}
            Type: {space.get('type', 'Unknown')}
            Description: {space.get('description', {}).get('plain', {}).get('value', 'No description')}
            """
        result.append(space_info)

    return "\n---\n".join(result) if result else "No spaces found"

@mcp.tool()
async def get_page_content(page_id: str) -> str:
    """Get the content of a specific Confluence page.
    
    Args:
        page_id: The ID of the Confluence page
    """
    url = f"{CONFLUENCE_BASE_URL}/content/{page_id}"
    params = {
        "expand": "body.storage,version,space,metadata.labels"
    }

    data = await make_confluence_request(url, params=params)
    if "error" in data:
        return data

    # Format the response
    title = data.get("title", "Unknown")
    space = data.get("space", {}).get("name", "Unknown")
    version = data.get("version", {}).get("number", "Unknown")
    content = data.get("body", {}).get("storage", {}).get("value", "No content")
    labels = [label.get("name") for label in data.get("metadata", {}).get("labels", {}).get("results", [])]

    return f"""
        Title: {title}
        Space: {space}
        Version: {version}
        Labels: {', '.join(labels) if labels else 'No labels'}

        Content:
        {content}
        """

@mcp.tool()
async def search_content(
    query: str,
    space_key: Optional[str] = None,
    limit: Optional[int] = 25,
    start: Optional[int] = 0
) -> str:
    """Search for content in Confluence.
    
    Args:
        query: Text to search for
        space_key: Optional space key to limit search to
        limit: Maximum number of results to return (default: 25)
        start: Index of the first result to return (for pagination)
    """
    url = f"{CONFLUENCE_BASE_URL}/content/search"
    
    cql = f'text ~ "{query}"'
    if space_key:
        cql += f' AND space.key = "{space_key}"'

    params = {
        "cql": cql,
        "limit": limit,
        "start": start,
        "expand": "space,version"
    }

    data = await make_confluence_request(url, params=params)
    if "error" in data:
        return data

    # Format the response
    result = []
    for content in data.get("results", []):
        content_info = f"""
Title: {content.get('title', 'Unknown')}
Type: {content.get('type', 'Unknown')}
Space: {content.get('space', {}).get('name', 'Unknown')}
ID: {content.get('id', 'Unknown')}
Last Updated: {content.get('version', {}).get('when', 'Unknown')}
"""
        result.append(content_info)

    return "\n---\n".join(result) if result else "No results found"

@mcp.tool()
async def list_pages_in_space(
    space_key: str,
    limit: Optional[int] = 25,
    start: Optional[int] = 0
) -> str:
    """List all pages in a Confluence space.
    
    Args:
        space_key: The key of the space to list pages from
        limit: Maximum number of pages to return (default: 25)
        start: Index of the first result to return (for pagination)
    """
    url = f"{CONFLUENCE_BASE_URL}/content"
    params = {
        "spaceKey": space_key,
        "type": "page",
        "limit": limit,
        "start": start,
        "expand": "version"
    }

    data = await make_confluence_request(url, params=params)
    if "error" in data:
        return data

    # Format the response
    result = []
    for page in data.get("results", []):
        page_info = f"""
Title: {page.get('title', 'Unknown')}
ID: {page.get('id', 'Unknown')}
Last Updated: {page.get('version', {}).get('when', 'Unknown')}
"""
        result.append(page_info)

    return "\n---\n".join(result) if result else f"No pages found in space {space_key}"

if __name__ == "__main__":
    # Add startup message
    print("Confluence MCP server starting...", file=sys.stderr)
    print("NOTE: Please ensure CONFLUENCE_BASE_URL, USERNAME, and API_TOKEN are set in your environment or .env file for the server to function correctly.", file=sys.stderr)
    # Initialize and run the server
    mcp.run(transport='stdio')
