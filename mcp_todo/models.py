"""Data models for MCP Planning server."""
import json
from enum import Enum
from pathlib import Path
from typing import Self, ForwardRef
from pydantic import BaseModel, Field

from mcp_todo.config import DATA_DIR


class TaskState(str, Enum):
    """Task state enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    
    def __str__(self) -> str:
        return self.value


class Task(BaseModel):
    """Task model representing a single task item."""
    description: str
    state: TaskState = TaskState.PENDING
    parent: "TaskList | None" = None
    subtasks: "TaskList | None" = None
    

    def add_task(self, description: str) -> "Task":
        """Add a new task to the sub-tasks."""
        if self.subtasks is None:
            self.subtasks = TaskList(parent_task=self)
        return self.subtasks.add_task(description)

    def model_post_init(self, __context):
        """Initialize subtasks after model initialization."""
        if self.subtasks is None:
            self.subtasks = TaskList(parent_task=self)
    
    def get_id(self, parent_id: str = "") -> str:
        """Generate the hierarchical ID for this task."""
        if not self.parent:
            return "1"
        
        # Find position in parent's task list
        if not self.parent.tasks:
            return "1"
        
        for i, task in enumerate(self.parent.tasks, 1):
            if task == self:
                if parent_id:
                    return f"{parent_id}.{i}"
                return str(i)
        
        # Fallback (should not happen)
        return "?"
    
    def delete(self, task_id: str) -> bool:
        """Delete a subtask by its ID.
        
        Args:
            task_id: The ID of the subtask to delete (e.g. "1" for the first subtask)
            
        Returns:
            True if the subtask was found and deleted, False otherwise
        """
        # Ensure subtasks is initialized
        if self.subtasks is None:
            return False
            
        # Try to delete the subtask by index
        try:
            index = int(task_id) - 1
            if 0 <= index < len(self.subtasks.tasks):
                # Remove the subtask
                self.subtasks.tasks.pop(index)
                return True
            return False
        except (ValueError, IndexError):
            return False
    
    def to_markdown(self, level: int = 0, parent_id: str = "") -> str:
        """Convert task to markdown format."""
        task_id = self.get_id(parent_id)
        checkbox = "x" if self.state == TaskState.COMPLETED else " "
        indent = "  " * level
        
        result = f"{indent}- [{checkbox}] {task_id}: {self.description}\n"
        
        # Add subtasks if they exist
        # subtasks should never be None due to model_post_init
        assert self.subtasks is not None, "subtasks should never be None"
        if self.subtasks.tasks:
            for subtask in self.subtasks.tasks:
                result += subtask.to_markdown(level + 1, task_id)
        
        return result
    
    def to_dict(self) -> dict:
        """Convert task to a dictionary without circular references."""
        return {
            "description": self.description,
            "state": self.state.value,
            "subtasks": self.subtasks.to_dict() if self.subtasks else None,
        }
    
    def __str__(self) -> str:
        return self.to_markdown()

    def __repr__(self) -> str:
        return self.to_markdown()
        
    def __eq__(self, other) -> bool:
        """Compare tasks for equality while avoiding parent recursion."""
        if not isinstance(other, Task):
            return False
            
        # Compare basic attributes
        if self.description != other.description or self.state != other.state:
            return False
            
        # Compare subtasks if both exist
        if self.subtasks is not None and other.subtasks is not None:
            # Compare subtasks without considering their parent references
            if len(self.subtasks.tasks) != len(other.subtasks.tasks):
                return False
                
            for i, task in enumerate(self.subtasks.tasks):
                if task != other.subtasks.tasks[i]:
                    return False
        elif self.subtasks is not None or other.subtasks is not None:
            # One has subtasks, the other doesn't
            return False
            
        return True
        
    def __getitem__(self, key: str | int) -> "Task | None":
        """Allow accessing subtasks by their ID using dictionary-like syntax.
        
        Examples:
            task["2"] will return the second subtask
            task[2] will return the second subtask
        """
        # Ensure subtasks is initialized
        if self.subtasks is None:
            return None
        # Delegate to TaskList's __getitem__
        return self.subtasks[key]


class TaskList(BaseModel):
    """Collection of tasks with persistence capabilities."""
    tasks: list[Task] = Field(default_factory=list)
    parent_task: Task | None = None
    
    def add_task(self, description: str) -> Task:
        """Add a new task to the list."""
        task = Task(description=description, parent=self)
        self.tasks.append(task)
        return task
    
    def get_task_by_id(self, task_id: str) -> Task | None:
        """Get a task by its hierarchical ID."""
        if not task_id or not self.tasks:
            return None
        
        # Parse the ID components
        id_parts = task_id.split(".")
        if not id_parts:
            return None
        
        # Get the first-level task
        try:
            index = int(id_parts[0]) - 1
            if index < 0 or index >= len(self.tasks):
                return None
            
            task = self.tasks[index]
            
            # If we have more parts, recursively search subtasks
            # subtasks should never be None due to model_post_init
            assert task.subtasks is not None, "subtasks should never be None"
            if len(id_parts) > 1:
                return task.subtasks.get_task_by_id(".".join(id_parts[1:]))
            
            return task
        except (ValueError, IndexError):
            return None
    
    def update_task_state(self, task_id: str, state: TaskState) -> bool:
        """Update the state of a task by its ID."""
        task = self.get_task_by_id(task_id)
        if task:
            task.state = state
            return True
        return False
    
    def delete(self, task_id: str) -> bool:
        """Delete a task by its ID.
        
        If the task has subtasks, they will be deleted recursively.
        Returns True if the task was found and deleted, False otherwise.
        """
        if not task_id or not self.tasks:
            return False
            
        # Parse the ID components
        id_parts = task_id.split(".")
        if not id_parts:
            return False
            
        # If we have a hierarchical ID, we need to find the parent task list
        if len(id_parts) > 1:
            # Get the parent task
            parent_id = ".".join(id_parts[:-1])
            parent_task = self.get_task_by_id(parent_id)
            
            if parent_task:
                # Delete from the parent task using the last part of the ID
                return parent_task.delete(id_parts[-1])
            return False
            
        # Handle direct child task (single-level ID)
        try:
            index = int(id_parts[0]) - 1
            if 0 <= index < len(self.tasks):
                # Remove the task
                self.tasks.pop(index)
                return True
            return False
        except (ValueError, IndexError):
            return False
    
    def save(self, user_id: str, session_id: str) -> Path:
        """Save the task list to disk."""
        # Create user and session directories
        user_dir = DATA_DIR / user_id
        session_dir = user_dir / session_id
        session_dir.mkdir(exist_ok=True, parents=True)

        # Save to task_list.json
        file_path = session_dir / "task_list.json"
        with open(file_path, "w") as f:
            # We need to exclude parent references to avoid circular references
            json_data = self.to_dict()
            f.write(json.dumps(json_data, indent=2))
        
        return file_path
    
    @classmethod
    def load(cls, user_id: str, session_id: str) -> Self:
        """Load a task list from disk."""
        file_path = DATA_DIR / user_id / session_id / "task_list.json"
        
        if not file_path.exists():
            return cls()
        
        with open(file_path, "r") as f:
            data = json.load(f)
        
        # Create a new task list
        task_list = cls()
        
        # Recursively create tasks from the loaded data
        def create_tasks(task_data_list, parent_list):
            for task_data in task_data_list:
                # Create the task
                task = Task(
                    description=task_data["description"],
                    state=TaskState(task_data["state"]),
                    parent=parent_list
                )
                parent_list.tasks.append(task)
                
                # Process subtasks if they exist
                if task_data.get("subtasks") and task_data["subtasks"].get("tasks"):
                    # subtasks should never be None due to model_post_init
                    assert task.subtasks is not None, "subtasks should never be None"
                    create_tasks(task_data["subtasks"]["tasks"], task.subtasks)
        
        # Start creating tasks from the root level
        if "tasks" in data:
            create_tasks(data["tasks"], task_list)
        
        return task_list
    
    def to_markdown(self) -> str:
        """Convert the entire task list to markdown format."""
        result = "# Task List\n\n"
        for task in self.tasks:
            result += task.to_markdown()
        return result

    def to_dict(self) -> dict:
        """Convert task to a dictionary without circular references."""
        return {
            "tasks": [task.to_dict() for task in self.tasks],
        }

    def __str__(self) -> str:
        return self.to_markdown()

    def __repr__(self) -> str:
        return self.to_markdown()
        
    def __eq__(self, other) -> bool:
        """Compare task lists for equality while avoiding parent recursion."""
        if not isinstance(other, TaskList):
            return False
            
        # Compare tasks list length
        if len(self.tasks) != len(other.tasks):
            return False
            
        # Compare each task in the list
        for i, task in enumerate(self.tasks):
            if task != other.tasks[i]:
                return False
                
        return True
        
    def __getitem__(self, key: str | int) -> Task | None:
        """Allow accessing tasks by their hierarchical ID using dictionary-like syntax.
        
        Examples:
            task_list["1.2.3"] will return the task with ID "1.2.3"
            task_list[1] will return the first task in the list
        """
        if isinstance(key, int):
            # Handle integer index (1-based to match task ID convention)
            try:
                return self.tasks[key - 1]
            except IndexError:
                return None
        else:
            # Handle string ID
            return self.get_task_by_id(key)

