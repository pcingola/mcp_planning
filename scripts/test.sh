#!/bin/bash -eu
set -o pipefail

# Source the config script
source "$(dirname "${BASH_SOURCE[0]}")/config.sh"

# Run all tests
cd "$PROJECT_DIR"
python -m unittest discover -s tests