"""MCP Planning server implementation."""
from fastmcp import FastMCP, Context, Image
from pathlib import Path

from mcp_planning.models import TaskList, Task, TaskState
from mcp_planning.config import DATA_DIR, SERVER_NAME


def get_session_id_tuple(ctx: Context | None) -> tuple[str, str]:
    """Get user_id and session_id from the context."""
    user_id = "default"
    session_id = "default"
    
    # In a real implementation, we would extract these from the context
    # For now, we'll use default values
    
    return user_id, session_id


# Initialize the MCP server
mcp = FastMCP(
    name=SERVER_NAME,
    instructions="A server for planning and managing agentic tasks as a to-do list."
)


@mcp.tool()
def add_task(description: str, ctx: Context | None = None) -> str:
    """Add a new task to the task list.
    
    Args:
        description: The description of the task
        ctx: The MCP context
        
    Returns:
        The ID of the newly created task
    """
    user_id, session_id = get_session_id_tuple(ctx)
    
    # Load existing tasks
    task_list = TaskList.load(user_id, session_id)
    
    # Add new task
    task = task_list.add_task(description)
    
    # Save tasks
    task_list.save(user_id, session_id)
    
    # Return the task ID
    return task.get_id()


@mcp.tool()
def add_subtask(parent_id: str, description: str, ctx: Context | None = None) -> str:
    """Add a subtask to an existing task.
    
    Args:
        parent_id: The ID of the parent task
        description: The description of the subtask
        ctx: The MCP context
        
    Returns:
        The ID of the newly created subtask
    """
    user_id, session_id = get_session_id_tuple(ctx)
    
    # Load existing tasks
    task_list = TaskList.load(user_id, session_id)
    
    # Find parent task
    parent_task = task_list.get_task_by_id(parent_id)
    if not parent_task:
        raise ValueError(f"Task with ID {parent_id} not found")
    
    # Add subtask
    if parent_task.subtasks is None:
        parent_task.subtasks = TaskList(parent_task=parent_task)
    
    subtask = parent_task.subtasks.add_task(description)
    
    # Save tasks
    task_list.save(user_id, session_id)
    
    # Return the subtask ID
    return subtask.get_id(parent_id)


@mcp.tool()
def update_task_state(task_id: str, state: TaskState, ctx: Context | None = None) -> bool:
    """Update the state of a task.
    
    Args:
        task_id: The ID of the task to update
        state: The new state of the task
        ctx: The MCP context
        
    Returns:
        True if the task was updated, False otherwise
    """
    user_id, session_id = get_session_id_tuple(ctx)
    
    # Load existing tasks
    task_list = TaskList.load(user_id, session_id)
    
    # Update task state
    success = task_list.update_task_state(task_id, state)
    
    if success:
        # Save tasks
        task_list.save(user_id, session_id)
    
    return success


@mcp.tool()
def delete_task(task_id: str, ctx: Context | None = None) -> bool:
    """Delete a task from the task list.
    
    Args:
        task_id: The ID of the task to delete
        ctx: The MCP context
        
    Returns:
        True if the task was deleted, False otherwise
    """
    user_id, session_id = get_session_id_tuple(ctx)
    
    # Load existing tasks
    task_list = TaskList.load(user_id, session_id)
    
    # Find the task
    task = task_list.get_task_by_id(task_id)
    if not task:
        return False
    
    # Find the parent task list
    parent = task.parent
    if not parent:
        # This is a top-level task
        if task in task_list.tasks:
            task_list.tasks.remove(task)
            task_list.save(user_id, session_id)
            return True
        return False
    
    # Remove from parent's tasks
    if task in parent.tasks:
        parent.tasks.remove(task)
        task_list.save(user_id, session_id)
        return True
    
    return False


@mcp.resource("tasks://{user_id}/{session_id}/list")
def get_tasks(user_id: str, session_id: str) -> str:
    """Get the task list as markdown.
    
    Args:
        user_id: The user ID
        session_id: The session ID
        
    Returns:
        The task list as markdown
    """
    # Load existing tasks
    task_list = TaskList.load(user_id, session_id)
    
    # Return as markdown
    return task_list.to_markdown()


@mcp.resource("tasks://{user_id}/{session_id}/data")
def get_tasks_data(user_id: str, session_id: str) -> dict:
    """Get the task list as JSON data.
    
    Args:
        user_id: The user ID
        session_id: The session ID
        
    Returns:
        The task list as JSON data
    """
    # Load existing tasks
    task_list = TaskList.load(user_id, session_id)
    
    # Return as JSON
    return task_list.model_dump(exclude={"tasks": {"__all__": {"parent"}}})


@mcp.tool()
def generate_task_graph(ctx: Context | None = None) -> Image:
    """Generate a visual graph of the task hierarchy.
    
    Args:
        ctx: The MCP context
        
    Returns:
        An image of the task graph
    """
    try:
        import matplotlib.pyplot as plt
        import networkx as nx
        import io
    except ImportError:
        raise RuntimeError("Required libraries not installed: matplotlib, networkx")
    
    user_id, session_id = get_session_id_tuple(ctx)
    
    # Load existing tasks
    task_list = TaskList.load(user_id, session_id)
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes and edges
    def add_task_to_graph(task: Task, parent_id: str = ""):
        task_id = task.get_id(parent_id)
        label = f"{task_id}: {task.description[:20]}..." if len(task.description) > 20 else f"{task_id}: {task.description}"
        
        # Add node with state as color
        color_map = {
            TaskState.PENDING: "lightblue",
            TaskState.IN_PROGRESS: "yellow",
            TaskState.COMPLETED: "lightgreen",
            TaskState.FAILED: "lightcoral"
        }
        
        G.add_node(task_id, label=label, color=color_map.get(task.state, "lightgray"))
        
        # Add edges to subtasks
        if task.subtasks and task.subtasks.tasks:
            for subtask in task.subtasks.tasks:
                subtask_id = subtask.get_id(task_id)
                G.add_edge(task_id, subtask_id)
                add_task_to_graph(subtask, task_id)
    
    # Add all tasks to the graph
    for task in task_list.tasks:
        add_task_to_graph(task)
    
    # If graph is empty, add a placeholder node
    if not G.nodes:
        G.add_node("No tasks", label="No tasks", color="white")
    
    # Create the plot
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G)
    
    # Draw nodes with colors
    node_colors = [G.nodes[node].get("color", "lightgray") for node in G.nodes]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2000, alpha=0.8)  # type: ignore
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, arrows=True)
    
    # Draw labels
    labels = {node: G.nodes[node].get("label", node) for node in G.nodes}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10)
    
    # Save to bytes
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close()
    
    # Return as image
    return Image(data=buf.getvalue(), format="png")


if __name__ == "__main__":
    # Run the server
    mcp.run(transport="streamable-http", host="127.0.0.1", port=9000)