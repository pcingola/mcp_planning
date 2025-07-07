from pydantic import BaseModel
from typing import Any
from uuid import uuid4

from .task import Task
from .task_state import TaskState


class TaskList(BaseModel):
    """A collection of tasks."""
    tasks: list[Task] = []
    
    def __str__(self) -> str:
        return f"TaskList(tasks={len(self.tasks)})"
    
    def add_task(self, description: str) -> Task:
        """Add a new task with the given description."""
        task = Task(id=str(uuid4()), description=description)
        self.tasks.append(task)
        return task
    
    def get_task_by_id(self, task_id: str) -> Task | None:
        """Get a task by its ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a task by its ID."""
        task = self.get_task_by_id(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False
    
    def get_tasks_by_state(self, state: TaskState) -> list[Task]:
        """Get all tasks with the specified state."""
        return [task for task in self.tasks if task.state == state]
