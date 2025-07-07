from enum import Enum


class TaskState(str, Enum):
    """Task states representing the current status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"