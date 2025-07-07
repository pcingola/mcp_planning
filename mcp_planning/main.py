#!/usr/bin/env python3
"""
Main entry point for the MCP Planning Server.
"""
from .server import mcp

if __name__ == "__main__":
    # Run the server
    mcp.run(transport="streamable-http")