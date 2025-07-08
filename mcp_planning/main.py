"""Main entry point for the MCP Planning server."""
import sys
from pathlib import Path

# Add the project directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the MCP server and configuration
from mcp_planning.server import mcp
from mcp_planning.config import SERVER_HOST, SERVER_PORT, SERVER_NAME


def main():
    """Run the MCP Planning server."""
    print(f"Starting MCP Planning server '{SERVER_NAME}'...")
    print(f"Server will be available at http://{SERVER_HOST}:{SERVER_PORT}")
    mcp.run(transport="streamable-http", host=SERVER_HOST, port=SERVER_PORT)


if __name__ == "__main__":
    main()