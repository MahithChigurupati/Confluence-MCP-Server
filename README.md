# Confluence MCP Server

A FastMCP-based server that provides seamless integration with Confluence's REST API, enabling programmatic access to Confluence spaces, pages, and content search functionality.

## Key Features

- **Space Management**: List and filter Confluence spaces
- **Page Operations**: Retrieve and manage page content
- **Search Functionality**: Execute CQL (Confluence Query Language) searches
- **Space Navigation**: List all pages within specific spaces
- **Authentication**: Secure API token-based access

## System Requirements

- Python 3.8+
- pip (Python package manager)
- Active Confluence instance with API access
- Valid Confluence API token

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/MahithChigurupati/Confluence-MCP-Server.git
   cd Confluence-MCP-Server
   ```

2. **Set Up Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   .\venv\Scripts\activate  # On Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Create Environment File**
   ```bash
   cp .env.example .env
   ```

2. **Configure Environment Variables**
   ```plaintext
   CONFLUENCE_BASE_URL=https://your-instance.atlassian.net/wiki/rest/api
   USERNAME=your.email@company.com
   API_TOKEN=your-api-token-here
   ```

3. **Obtain Confluence API Token**
   1. Visit [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
   2. Click "Create API Token"
   3. Enter a meaningful label (e.g., "MCP Server Access")
   4. Copy the generated token immediately (it won't be shown again)

## Usage Guide

### Starting the Server
```bash
python confluence.py
```

### Available API Methods

#### 1. List Spaces
```python
response = await list_spaces(
    query="engineering",  # Optional: Filter spaces by name
    limit=25,            # Optional: Maximum number of spaces to return
    start=0             # Optional: Starting index for pagination
)
```

#### 2. Get Page Content
```python
response = await get_page_content(
    page_id="123456",   # Required: Confluence page ID
    version=2           # Optional: Specific version number
)
```

#### 3. Search Content
```python
response = await search_content(
    query="project plan",    # Required: Search query
    space_key="TEAM",       # Optional: Limit search to specific space
    limit=50,               # Optional: Maximum results
    start=0                 # Optional: Starting index
)
```

#### 4. List Pages in Space
```python
response = await list_pages_in_space(
    space_key="TEAM",       # Required: Space key
    limit=100,             # Optional: Maximum pages to return
    start=0               # Optional: Starting index
)
```

## Integration with MCP Clients

### Claude Desktop Configuration
```json
{
  "mcpServers": {
    "confluence": {
      "command": "python path",
      "args": ["/path/to/Confluence-MCP-Server/confluence.py"]
    }
  }
}
```

Location: `~/.claude/claude_desktop_config.json` (macOS/Linux) or `%USERPROFILE%\.claude\config.json` (Windows)

### Cursor Configuration
```json
{
  "mcpServers": {
    "confluence": {
      "command": "python path",
      "args": ["/path/to/Confluence-MCP-Server/confluence.py"]
    }
  }
}
```

use `which python` to find python path

use `pwd` inside cloned repository to get the path. Don't forget to add `confluence.py` in the end.

Location: `~/.cursor/mcp.json` (macOS/Linux) or `%USERPROFILE%\.cursor\config.json` (Windows)

## Error Handling

Common error codes and their meanings:

- `401`: Invalid API token or credentials
- `403`: Insufficient permissions
- `404`: Resource not found
- `429`: Rate limit exceeded

## Troubleshooting

1. **Connection Issues**
   - Verify CONFLUENCE_BASE_URL format
   - Check network connectivity
   - Confirm API token validity

2. **Authentication Errors**
   - Ensure USERNAME matches Atlassian account email
   - Verify API_TOKEN is correctly copied
   - Check for special characters in .env file

3. **Permission Errors**
   - Confirm user has required Confluence permissions
   - Verify space and page access rights

## Support

For issues and feature requests, please create an issue in the repository's issue tracker.

## License

MIT License. See `LICENSE` file for full terms.