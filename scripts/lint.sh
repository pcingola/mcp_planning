#!/bin/bash -eu
set -o pipefail

# Source the config script
source "$(dirname "${BASH_SOURCE[0]}")/config.sh"

# Run ruff on the project
cd "$PROJECT_DIR"
ruff check mcp_planning