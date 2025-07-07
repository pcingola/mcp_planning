#!/bin/bash -eu
set -o pipefail

# Source the config script
source "$(dirname "${BASH_SOURCE[0]}")/config.sh"

# Run the MCP Planning Server
cd "$PROJECT_DIR"
python -m mcp_planning.main