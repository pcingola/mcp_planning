"""
FastMCP server for planning Agentic tasks.
Provides tools for managing task lists with user/session isolation.
"""

import logging
from fastmcp import FastMCP, Context
from fastmcp.server import dependencies

from mcp_planning.config import SERVER_NAME, SERVER_HOST, SERVER_PORT
from mcp_planning.models import TaskList, TaskState
from mcp_planning.utils import get_session_id_tuple

# Set up logging
logger = logging.getLogger(__name__)

# Initialize the MCP server
mcp = FastMCP(
    name=SERVER_NAME,
    instructions="Planning server for managing task lists. All task lists are private to the user/session. Task IDs are hierarchical (e.g. '1.3.2' means task 2 under task 3 under task 1).",
)

# Cache for task lists to avoid loading from disk on every request
# This is a simple in-memory cache keyed by (user_id, session_id)
task_list_cache = {}


def get_task_list(ctx: Context | None = None) -> TaskList:
    """
    Get the task list for the current user and session.
    If the task list is not in the cache, load it from disk.
    """
    user_id, session_id = get_session_id_tuple(ctx)
    cache_key = (user_id, session_id)
    
    if cache_key not in task_list_cache:
        task_list_cache[cache_key] = TaskList.load(user_id, session_id)
    
    return task_list_cache[cache_key]


def save_task_list(task_list: TaskList, ctx: Context | None = None) -> None:
    """
    Save the task list to disk and update the cache.
    """
    user_id, session_id = get_session_id_tuple(ctx)
    cache_key = (user_id, session_id)
    
    # Save to disk
    task_list.save(user_id, session_id)
    
    # Update cache
    task_list_cache[cache_key] = task_list


@mcp.tool()
def add_task(description: str, parent_task_id: str | None = None, ctx: Context | None = None) -> str:
    """
    Add a new task to the user's task list.
    
    Args:
        description: The description of the task to add
        parent_task_id: The ID of the parent task to add this task under (optional, e.g. parent_task_id="1.3")
        
    Returns:
        The ID of the newly created task (e.g. "1.3.2") or an error message if the parent task ID is invalid.
    """
    # Get the task list for this user/session
    task_list = get_task_list(ctx)
    
    # Add the task
    if parent_task_id:
        parent_task = task_list.get_task_by_id(parent_task_id)
        if not parent_task:
            # Provide a clean error message without stack trace
            return f"ERROR: Parent task with ID '{parent_task_id}' not found."
        task = parent_task.add_task(description)
        # For subtasks, we need to return the full hierarchical ID
        task_id = f"{parent_task_id}.{task.get_id()}"
    else:
        task = task_list.add_task(description)
        task_id = task.get_id()

    # Save the updated task list
    save_task_list(task_list, ctx)
    
    # Return the task ID
    return task_id


@mcp.tool()
def show_task_list(ctx: Context | None = None) -> str:
    """
    Show all tasks in the user's task list as markdown.

    Returns:
        Markdown representation of the task list
    """
    # Get the task list for this user/session
    task_list = get_task_list(ctx)
    
    # Return the markdown representation
    return task_list.to_markdown()


@mcp.tool()
def delete_task(task_id: str, ctx: Context | None = None) -> bool:
    """
    Delete a task from the user's task list by ID.
    
    Args:
        task_id: The ID of the task to delete (e.g. "1.3.2")
        
    Returns:
        True if the task was deleted, False otherwise
    """
    # Get the task list for this user/session
    task_list = get_task_list(ctx)
    
    # Delete the task
    success = task_list.delete(task_id)
    
    # Save the updated task list if the task was deleted
    if success:
        save_task_list(task_list, ctx)
    
    return success


@mcp.tool()
def update_task_status(task_id: str, status: str, ctx: Context | None = None) -> bool:
    """
    Update the status of a task by ID.
    
    Args:
        task_id: The ID of the task to update (e.g. "3.2")
        status: The new status (pending, in_progress, completed, failed)
        
    Returns:
        True if the task was updated, False otherwise
    """
    # Get the task list for this user/session
    task_list = get_task_list(ctx)
    
    try:
        # Convert the status string to TaskState enum
        task_state = TaskState(status)
        
        # Update the task state
        success = task_list.update_task_state(task_id, task_state)
        
        # Save the updated task list if the task was updated
        if success:
            save_task_list(task_list, ctx)
        
        return success
    except ValueError:
        # Invalid status value
        return False


if __name__ == "__main__":
    # Run the server with streamable HTTP transport
    mcp.run(transport="http", host=SERVER_HOST, port=SERVER_PORT)