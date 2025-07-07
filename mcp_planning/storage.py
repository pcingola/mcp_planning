import json
from pathlib import Path
from typing import Optional

from .config import DATA_DIR
from .task_list import TaskList


class Storage:
    """Handles persistence of task lists to the filesystem."""
    
    def __init__(self, base_dir: Path = DATA_DIR):
        """Initialize the storage with a base directory."""
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def __str__(self) -> str:
        return f"Storage(base_dir={self.base_dir})"
    
    def get_user_session_dir(self, user_id: str, session_id: str) -> Path:
        """Get the directory for a specific user and session."""
        return self.base_dir / user_id / session_id
    
    def get_task_file_path(self, user_id: str, session_id: str) -> Path:
        """Get the file path for storing tasks for a specific user and session."""
        user_session_dir = self.get_user_session_dir(user_id, session_id)
        return user_session_dir / "tasks.json"
    
    def save_task_list(self, task_list: TaskList, user_id: str, session_id: str) -> None:
        """Save a task list to the filesystem."""
        user_session_dir = self.get_user_session_dir(user_id, session_id)
        user_session_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = self.get_task_file_path(user_id, session_id)
        with open(file_path, "w") as f:
            f.write(task_list.model_dump_json(indent=2))
    
    def load_task_list(self, user_id: str, session_id: str) -> Optional[TaskList]:
        """Load a task list from the filesystem."""
        file_path = self.get_task_file_path(user_id, session_id)
        
        if not file_path.exists():
            return None
        
        with open(file_path, "r") as f:
            data = json.load(f)
            return TaskList.model_validate(data)
    
    def delete_task_list(self, user_id: str, session_id: str) -> bool:
        """Delete a task list from the filesystem."""
        file_path = self.get_task_file_path(user_id, session_id)
        
        if not file_path.exists():
            return False
        
        file_path.unlink()
        return True
    
    def get_or_create_task_list(self, user_id: str, session_id: str) -> TaskList:
        """Get an existing task list or create a new one if it doesn't exist."""
        task_list = self.load_task_list(user_id, session_id)
        if task_list is None:
            task_list = TaskList()
        return task_list
    
    def list_user_sessions(self, user_id: str) -> list[str]:
        """List all session IDs for a specific user."""
        user_dir = self.base_dir / user_id
        
        if not user_dir.exists() or not user_dir.is_dir():
            return []
        
        return [session_dir.name for session_dir in user_dir.iterdir() 
                if session_dir.is_dir() and (session_dir / "tasks.json").exists()]
    
    def list_users(self) -> list[str]:
        """List all user IDs that have stored task lists."""
        if not self.base_dir.exists() or not self.base_dir.is_dir():
            return []
        
        return [user_dir.name for user_dir in self.base_dir.iterdir() 
                if user_dir.is_dir() and any(session_dir.is_dir() and (session_dir / "tasks.json").exists() 
                                            for session_dir in user_dir.iterdir())]