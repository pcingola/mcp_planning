"""Configuration for MCP Planning server."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Server configuration
SERVER_NAME = os.getenv("SERVER_NAME", "PlanningServer")
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "9000"))

# Base directories
PROJECT_DIR = Path(__file__).parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", PROJECT_DIR / "data"))

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True, parents=True)