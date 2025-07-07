from pydantic import BaseModel
from typing import Any
from uuid import uuid4

from .task_state import TaskState


class Task(BaseModel):
    """Represents a task with optional subtasks."""
    id: str
    description: str
    state: TaskState = TaskState.PENDING
    subtasks: list["Task"] = []
    
    def __str__(self) -> str:
        return f"Task({self.id}, {self.description}, {self.state}, subtasks={len(self.subtasks)})"
    
    def add_subtask(self, description: str) -> "Task":
        """Add a new subtask with the given description."""
        subtask = Task(id=str(uuid4()), description=description)
        self.subtasks.append(subtask)
        return subtask
    
    def mark_in_progress(self) -> None:
        """Mark the task as in progress."""
        self.state = TaskState.IN_PROGRESS
    
    def mark_completed(self) -> None:
        """Mark the task as completed."""
        self.state = TaskState.COMPLETED
    
    def mark_failed(self) -> None:
        """Mark the task as failed."""
        self.state = TaskState.FAILED
    
    def get_subtasks_by_state(self, state: TaskState) -> list["Task"]:
        """Get all subtasks with the specified state."""
        return [task for task in self.subtasks if task.state == state]