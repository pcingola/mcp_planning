# MCP Planning Server

## Project Goals

The MCP Planning Server is designed to provide a simple yet powerful task management system through the Model Context Protocol (MCP). It enables AI agents and other clients to create, track, and manage hierarchical tasks with state tracking.

The primary goals of this project are:

1. Provide a clean API for task management through MCP tools
2. Enable persistent storage of tasks with user and session isolation
3. Support hierarchical task structures with subtasks
4. Track task state transitions (pending, in-progress, completed, failed)

## Project Structure

The project is organized as follows:

- `mcp_planning/`: Main package directory
  - `config.py`: Configuration settings and constants
  - `task_state.py`: Enum defining possible task states
  - `task.py`: Task model with methods for state management
  - `task_list.py`: Collection of tasks with management methods
  - `storage.py`: Handles persistence of task lists to the filesystem
  - `server.py`: MCP server implementation with tools and resources
  - `main.py`: Entry point for running the server

- `scripts/`: Shell scripts for common operations
  - `config.sh`: Environment setup and configuration
  - `run.sh`: Script to run the server
  - `lint.sh`: Script to run linting
  - `test.sh`: Script to run all tests
  - `test_unit.sh`: Script to run unit tests
  - `test_integration.sh`: Script to run integration tests

- `tests/`: Test directory
  - `unit/`: Unit tests
  - `integration/`: Integration tests
  - `data/`: Test data

The server uses a simple file-based storage system that organizes task data by user ID and session ID, allowing for isolation between different users and sessions.