import unittest
import tempfile
import shutil
from pathlib import Path

from mcp_planning.storage import Storage
from mcp_planning.task_list import TaskList


class TestStorage(unittest.TestCase):
    """Test cases for the Storage class."""
    
    def setUp(self):
        """Set up a temporary directory for testing."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.storage = Storage(base_dir=self.temp_dir)
        self.user_id = "test_user"
        self.session_id = "test_session"
    
    def tearDown(self):
        """Clean up the temporary directory after testing."""
        shutil.rmtree(self.temp_dir)
    
    def test_save_and_load_task_list(self):
        """Test saving and loading a task list."""
        # Create a task list with a task
        task_list = TaskList()
        task = task_list.add_task("Test task")
        
        # Save the task list
        self.storage.save_task_list(task_list, self.user_id, self.session_id)
        
        # Check that the file exists
        file_path = self.storage.get_task_file_path(self.user_id, self.session_id)
        self.assertTrue(file_path.exists())
        
        # Load the task list
        loaded_task_list = self.storage.load_task_list(self.user_id, self.session_id)
        
        # Check that the loaded task list has the same task
        self.assertIsNotNone(loaded_task_list)
        self.assertEqual(len(loaded_task_list.tasks), 1)
        self.assertEqual(loaded_task_list.tasks[0].description, "Test task")
        self.assertEqual(loaded_task_list.tasks[0].id, task.id)
    
    def test_delete_task_list(self):
        """Test deleting a task list."""
        # Create and save a task list
        task_list = TaskList()
        task_list.add_task("Test task")
        self.storage.save_task_list(task_list, self.user_id, self.session_id)
        
        # Delete the task list
        result = self.storage.delete_task_list(self.user_id, self.session_id)
        self.assertTrue(result)
        
        # Check that the file no longer exists
        file_path = self.storage.get_task_file_path(self.user_id, self.session_id)
        self.assertFalse(file_path.exists())
        
        # Try to delete a non-existent task list
        result = self.storage.delete_task_list(self.user_id, "non_existent_session")
        self.assertFalse(result)
    
    def test_list_user_sessions(self):
        """Test listing user sessions."""
        # Create and save task lists for different sessions
        task_list = TaskList()
        self.storage.save_task_list(task_list, self.user_id, "session1")
        self.storage.save_task_list(task_list, self.user_id, "session2")
        
        # List the sessions
        sessions = self.storage.list_user_sessions(self.user_id)
        self.assertEqual(len(sessions), 2)
        self.assertIn("session1", sessions)
        self.assertIn("session2", sessions)
        
        # List sessions for a non-existent user
        sessions = self.storage.list_user_sessions("non_existent_user")
        self.assertEqual(len(sessions), 0)
    
    def test_list_users(self):
        """Test listing users."""
        # Create and save task lists for different users
        task_list = TaskList()
        self.storage.save_task_list(task_list, "user1", "session1")
        self.storage.save_task_list(task_list, "user2", "session1")
        
        # List the users
        users = self.storage.list_users()
        self.assertEqual(len(users), 2)
        self.assertIn("user1", users)
        self.assertIn("user2", users)


if __name__ == "__main__":
    unittest.main()