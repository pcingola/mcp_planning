import unittest

from mcp_planning.task_list import TaskList
from mcp_planning.task import Task
from mcp_planning.task_state import TaskState


class TestTaskList(unittest.TestCase):
    """Test cases for the TaskList class."""
    
    def setUp(self):
        """Set up a task list for testing."""
        self.task_list = TaskList()
    
    def test_str_empty_list(self):
        """Test the string representation of an empty task list."""
        expected = "# Task List\n\nNo tasks yet."
        self.assertEqual(str(self.task_list), expected)
    
    def test_str_with_tasks(self):
        """Test the string representation of a task list with tasks."""
        # Add tasks with different states
        task1 = self.task_list.add_task("Complete project")
        task2 = self.task_list.add_task("Write documentation")
        task3 = self.task_list.add_task("Submit report")
        
        # Mark task2 as completed
        task2.mark_completed()
        
        # Expected markdown output
        expected = (
            "# Task List\n"
            "- [ ] **1**: Complete project\n"
            "- [x] **2**: Write documentation\n"
            "- [ ] **3**: Submit report"
        )
        
        self.assertEqual(str(self.task_list), expected)
    
    def test_str_with_subtasks(self):
        """Test the string representation of a task list with subtasks."""
        # Add a task with subtasks
        task = self.task_list.add_task("Main task")
        subtask1 = task.add_subtask("Subtask 1")
        subtask2 = task.add_subtask("Subtask 2")
        
        # Mark subtask1 as completed
        subtask1.mark_completed()
        
        # Expected markdown output
        expected = (
            "# Task List\n"
            "- [ ] **1**: Main task\n"
            "  - [x] **1.1**: Subtask 1\n"
            "  - [ ] **1.2**: Subtask 2"
        )
        
        self.assertEqual(str(self.task_list), expected)
    
    def test_repr(self):
        """Test the repr representation of a task list."""
        # Empty task list
        self.assertEqual(repr(self.task_list), "TaskList(tasks=0)")
        
        # Add some tasks
        self.task_list.add_task("Task 1")
        self.task_list.add_task("Task 2")
        
        # Check repr with tasks
        self.assertEqual(repr(self.task_list), "TaskList(tasks=2)")


if __name__ == "__main__":
    unittest.main()