from fastmcp import Context, FastMCP
from typing import Any

from mcp_planning.utils import get_session_id_tuple

from mcp_planning.storage import Storage
from mcp_planning.task import Task
from mcp_planning.task_list import TaskList
from mcp_planning.task_state import TaskState


# Initialize the MCP server
mcp = FastMCP(
    name="To do Server",
    instructions="A server for managing task planning as a 'to do' list. Use this to create, update, and track tasks."
)

# Initialize the storage
storage = Storage()


@mcp.tool()
def add_task(ctx: Context, description: str) -> Task:
    """Add a new task with the given description."""
    user_id, session_id = get_session_id_tuple(ctx)
    task_list = storage.get_or_create_task_list(user_id, session_id)
    
    task = task_list.add_task(description)
    storage.save_task_list(task_list, user_id, session_id)
    
    return task


@mcp.tool()
def get_tasks(ctx: Context, state: str | None = None) -> list[Task]:
    """
    Get all tasks, optionally filtered by state.
    
    Args:
        state: Filter tasks by state (pending, in_progress, completed, failed)
    """
    user_id, session_id = get_session_id_tuple(ctx)
    task_list = storage.get_or_create_task_list(user_id, session_id)
    
    if state:
        try:
            task_state = TaskState(state)
            return task_list.get_tasks_by_state(task_state)
        except ValueError:
            raise ValueError(f"Invalid state: {state}. Must be one of: {', '.join([s.value for s in TaskState])}")
    
    return task_list.tasks


@mcp.tool()
def get_task(ctx: Context, task_id: str) -> Task | None:
    """Get a task by its ID."""
    user_id, session_id = get_session_id_tuple(ctx)
    task_list = storage.get_or_create_task_list(user_id, session_id)
    
    task = task_list.get_task_by_id(task_id)
    if not task:
        raise ValueError(f"Task with ID {task_id} not found")
    
    return task


@mcp.tool()
def update_task_state(ctx: Context, task_id: str, state: str) -> Task:
    """
    Update a task's state.
    
    Args:
        task_id: The ID of the task to update
        state: The new state (pending, in_progress, completed, failed)
    """
    user_id, session_id = get_session_id_tuple(ctx)
    task_list = storage.get_or_create_task_list(user_id, session_id)
    
    task = task_list.get_task_by_id(task_id)
    if not task:
        raise ValueError(f"Task with ID {task_id} not found")
    
    try:
        task_state = TaskState(state)
    except ValueError:
        raise ValueError(f"Invalid state: {state}. Must be one of: {', '.join([s.value for s in TaskState])}")
    
    if task_state == TaskState.IN_PROGRESS:
        task.mark_in_progress()
    elif task_state == TaskState.COMPLETED:
        task.mark_completed()
    elif task_state == TaskState.FAILED:
        task.mark_failed()
    else:  # PENDING
        task.state = TaskState.PENDING
    
    storage.save_task_list(task_list, user_id, session_id)
    return task


@mcp.tool()
def delete_task(ctx: Context, task_id: str) -> bool:
    """Delete a task by its ID."""
    user_id, session_id = get_session_id_tuple(ctx)
    task_list = storage.get_or_create_task_list(user_id, session_id)
    
    result = task_list.remove_task(task_id)
    if result:
        storage.save_task_list(task_list, user_id, session_id)
    
    return result


@mcp.tool()
def add_subtask(ctx: Context, parent_task_id: str, description: str) -> Task:
    """Add a subtask to an existing task."""
    user_id, session_id = get_session_id_tuple(ctx)
    task_list = storage.get_or_create_task_list(user_id, session_id)
    
    parent_task = task_list.get_task_by_id(parent_task_id)
    if not parent_task:
        raise ValueError(f"Parent task with ID {parent_task_id} not found")
    
    subtask = parent_task.add_subtask(description)
    storage.save_task_list(task_list, user_id, session_id)
    
    return subtask


@mcp.resource("tasks://{user_id}/{session_id}")
def get_task_list_resource(user_id: str, session_id: str) -> TaskList | None:
    """Get the task list for a specific user and session."""
    return storage.load_task_list(user_id, session_id)


@mcp.resource("tasks://sessions/{user_id}")
def get_user_sessions(user_id: str) -> list[str]:
    """Get all session IDs for a specific user."""
    return storage.list_user_sessions(user_id)


@mcp.resource("tasks://users")
def get_users() -> list[str]:
    """Get all user IDs that have stored task lists."""
    return storage.list_users()


if __name__ == "__main__":
    # Run the server
    mcp.run(transport="streamable-http")