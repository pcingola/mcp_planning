# MCP Planning Server

An MCP server for planning Agentic tasks, similar to a "to do" list.

## Overview

This project implements a Model Context Protocol (MCP) server that provides tools for managing task planning. It allows users to create, update, and track tasks in a hierarchical structure.

## Features

- Create and manage tasks with subtasks
- Track task state (pending, in-progress, completed, failed)
- Persistent storage of tasks in JSON format
- User and session isolation for task data
- MCP tools for task management

## Installation

1. Clone the repository
2. Install dependencies using uv:

```bash
uv pip install -e .
```

## Usage

### Running the server

```bash
./scripts/run.sh
```

This will start the MCP server on the configured host and port (default: 127.0.0.1:9000).

### MCP Tools

The server provides the following MCP tools:

- `add_task`: Add a new task
- `get_tasks`: Get all tasks, optionally filtered by state
- `get_task`: Get a specific task by ID
- `update_task_state`: Update a task's state
- `delete_task`: Delete a task
- `add_subtask`: Add a subtask to an existing task

### MCP Resources

The server provides the following MCP resources:

- `tasks://{user_id}/{session_id}`: Get the task list for a specific user and session
- `tasks://sessions/{user_id}`: Get all session IDs for a specific user
- `tasks://users`: Get all user IDs that have stored task lists

## Development

### Running tests

```bash
./scripts/test.sh
```

### Running linting

```bash
./scripts/lint.sh
```

## License

[MIT](LICENSE)
