"""Unit tests for the TaskList model."""
import unittest
import tempfile
import shutil
from pathlib import Path
from typing import cast

from mcp_todo.models import Task, TaskList, TaskState
from mcp_todo.config import DATA_DIR


class TestTaskListModel(unittest.TestCase):
    """Test cases for the TaskList model."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test data
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_data_dir = DATA_DIR
        
        # Override DATA_DIR for testing
        import mcp_todo.config
        mcp_todo.config.DATA_DIR = self.temp_dir
        
        # Create a task list with some tasks
        self.task_list = TaskList()
        self.task1 = self.task_list.add_task("Task 1")
        self.task2 = self.task_list.add_task("Task 2")
        
        # Add a subtask to task1
        task1_subtasks = cast(TaskList, self.task1.subtasks)
        self.subtask1 = task1_subtasks.add_task("Subtask 1.1")
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Restore original DATA_DIR
        import mcp_todo.config
        mcp_todo.config.DATA_DIR = self.original_data_dir
        
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_add_task(self):
        """Test adding tasks to a task list."""
        task_list = TaskList()
        
        # Add a task
        task = task_list.add_task("New task")
        
        # Check that the task was added correctly
        self.assertEqual(len(task_list.tasks), 1)
        self.assertEqual(task_list.tasks[0], task)
        self.assertEqual(task.description, "New task")
        self.assertEqual(task.parent, task_list)
    
    def test_get_task_by_id(self):
        """Test retrieving tasks by ID."""
        # Check top-level tasks
        task1 = self.task_list.get_task_by_id("1")
        self.assertEqual(task1, self.task1)
        
        task2 = self.task_list.get_task_by_id("2")
        self.assertEqual(task2, self.task2)
        
        # Check subtasks
        subtask1 = self.task_list.get_task_by_id("1.1")
        self.assertEqual(subtask1, self.subtask1)
        
        # Check non-existent tasks
        self.assertIsNone(self.task_list.get_task_by_id("3"))
        self.assertIsNone(self.task_list.get_task_by_id("1.2"))
    
    def test_update_task_state(self):
        """Test updating task states."""
        # Update a task state
        self.task_list.update_task_state("1", TaskState.IN_PROGRESS)
        self.assertEqual(self.task1.state, TaskState.IN_PROGRESS)
        
        # Update a subtask state
        self.task_list.update_task_state("1.1", TaskState.COMPLETED)
        self.assertEqual(self.subtask1.state, TaskState.COMPLETED)
        
        # Try to update a non-existent task
        result = self.task_list.update_task_state("3", TaskState.FAILED)
        self.assertFalse(result)
    
    def test_save_and_load(self):
        """Test saving and loading task lists."""
        # Save the task list
        user_id = "test_user"
        session_id = "test_session"
        file_path = self.task_list.save(user_id, session_id)
        
        # Check that the file was created
        self.assertTrue(file_path.exists())
        
        # Load the task list
        loaded_task_list = TaskList.load(user_id, session_id)
        
        # Check that the loaded task list has the same structure
        self.assertEqual(len(loaded_task_list.tasks), 2)
        self.assertEqual(loaded_task_list.tasks[0].description, "Task 1")
        self.assertEqual(loaded_task_list.tasks[1].description, "Task 2")
        
        # Check subtasks - use cast to help Pylance
        task1_subtasks = cast(TaskList, loaded_task_list.tasks[0].subtasks)
        self.assertEqual(len(task1_subtasks.tasks), 1)
        self.assertEqual(task1_subtasks.tasks[0].description, "Subtask 1.1")
    
    def test_to_markdown(self):
        """Test converting a task list to markdown."""
        # Generate markdown
        markdown = self.task_list.to_markdown()
        
        # Check that the markdown contains the expected content
        self.assertIn("# Task List", markdown)
        self.assertIn("- [ ] 1: Task 1", markdown)
        self.assertIn("- [ ] 2: Task 2", markdown)
        self.assertIn("- [ ] 1.1: Subtask 1.1", markdown)


    def test_delete_task_and_renumber(self):
        """Test deleting a task and checking that IDs are renumbered correctly."""
        # Create a task list with 10 items
        task_list = TaskList()
        for i in range(1, 11):
            task_list.add_task(f"Main Task {i}")
        
        # Add nested tasks to create "1.1.1" and "1.1.2"
        task1 = task_list.get_task_by_id("1")
        self.assertIsNotNone(task1)
        assert task1 is not None  # For Pylance
        
        # Add subtask 1.1
        self.assertIsNotNone(task1.subtasks)
        assert task1.subtasks is not None  # For Pylance
        subtask1 = task1.subtasks.add_task("Subtask 1.1")
        
        # Add subtasks 1.1.1 and 1.1.2
        self.assertIsNotNone(subtask1.subtasks)
        assert subtask1.subtasks is not None  # For Pylance
        subsubtask1 = subtask1.subtasks.add_task("Nested Task 1.1.1")
        subsubtask2 = subtask1.subtasks.add_task("Nested Task 1.1.2")
        
        # Show the markdown and check it
        markdown = task_list.to_markdown()
        self.assertIn("# Task List", markdown)
        self.assertIn("- [ ] 1: Main Task 1", markdown)
        self.assertIn("- [ ] 1.1: Subtask 1.1", markdown)
        self.assertIn("- [ ] 1.1.1: Nested Task 1.1.1", markdown)
        self.assertIn("- [ ] 1.1.2: Nested Task 1.1.2", markdown)
        
        # Delete item "1.1.1" using the new delete method
        task_list.delete("1.1.1")
        
        # Check that the new item "1.1.1" is the former "1.1.2"
        updated_markdown = task_list.to_markdown()
        self.assertIn("- [ ] 1.1.1: Nested Task 1.1.2", updated_markdown)
        self.assertNotIn("- [ ] 1.1.2:", updated_markdown)
        
        # Verify the task ID has been updated
        updated_subsubtask = subtask1.subtasks.get_task_by_id("1")
        self.assertIsNotNone(updated_subsubtask)
        assert updated_subsubtask is not None  # For Pylance
        self.assertEqual(updated_subsubtask.description, "Nested Task 1.1.2")
        self.assertEqual(updated_subsubtask.get_id("1.1"), "1.1.1")


    def test_delete_method(self):
        """Test the delete method for tasks and subtasks."""
        # Create a task list with some tasks
        task_list = TaskList()
        task1 = task_list.add_task("Task 1")
        task2 = task_list.add_task("Task 2")
        task3 = task_list.add_task("Task 3")
        
        # Add subtasks to task1
        subtask1 = task1.add_task("Subtask 1.1")
        subtask2 = task1.add_task("Subtask 1.2")
        
        # Add a nested subtask
        nested_subtask = subtask1.add_task("Nested 1.1.1")
        
        # Test deleting a top-level task
        self.assertTrue(task_list.delete("2"))
        self.assertEqual(len(task_list.tasks), 2)
        self.assertEqual(task_list.tasks[0].description, "Task 1")
        self.assertEqual(task_list.tasks[1].description, "Task 3")
        
        # Check that IDs are updated
        self.assertEqual(task_list.tasks[1].get_id(), "2")
        
        # Test deleting a subtask
        self.assertTrue(task_list.delete("1.2"))
        subtasks = task1.subtasks
        self.assertIsNotNone(subtasks)
        assert subtasks is not None  # For Pylance
        self.assertEqual(len(subtasks.tasks), 1)
        self.assertEqual(subtasks.tasks[0].description, "Subtask 1.1")
        
        # Test deleting a nested subtask
        self.assertTrue(task_list.delete("1.1.1"))
        nested_subtasks = subtask1.subtasks
        self.assertIsNotNone(nested_subtasks)
        assert nested_subtasks is not None  # For Pylance
        self.assertEqual(len(nested_subtasks.tasks), 0)
        
        # Test deleting non-existent tasks
        self.assertFalse(task_list.delete("4"))  # Non-existent top-level
        self.assertFalse(task_list.delete("1.3"))  # Non-existent subtask
        self.assertFalse(task_list.delete("1.1.2"))  # Non-existent nested subtask
        
    def test_task_list_equality(self):
        """Test that task lists are compared correctly for equality."""
        # Create two empty task lists
        task_list1 = TaskList()
        task_list2 = TaskList()
        
        # Empty lists should be equal
        self.assertEqual(task_list1, task_list2)
        
        # Add identical tasks to both lists
        task1_1 = task_list1.add_task("Task 1")
        task1_2 = task_list1.add_task("Task 2")
        
        task2_1 = task_list2.add_task("Task 1")
        task2_2 = task_list2.add_task("Task 2")
        
        # Lists with identical tasks should be equal
        self.assertEqual(task_list1, task_list2)
        
        # Add a subtask to one list but not the other
        task1_1.add_task("Subtask 1.1")
        self.assertNotEqual(task_list1, task_list2)
        
        # Make the lists identical again
        task2_1.add_task("Subtask 1.1")
        self.assertEqual(task_list1, task_list2)
        
        # Test that parent_task references don't cause infinite recursion
        task = Task(description="Parent")
        task_list3 = TaskList(parent_task=task)
        task_list4 = TaskList()
        
        # Even though one has a parent_task and the other doesn't,
        # they should be equal if their tasks are the same
        self.assertEqual(task_list3, task_list4)
        
        # Add different tasks to make them not equal
        task_list3.add_task("Task in list 3")
        self.assertNotEqual(task_list3, task_list4)


    def test_delete_subtask_specific(self):
        """Test specifically for deleting subtasks with hierarchical IDs."""
        # Create a task list with a parent task
        task_list = TaskList()
        parent_task = task_list.add_task("Parent Task")
        
        # Add two subtasks
        subtask1 = parent_task.add_task("Subtask to keep")
        subtask2 = parent_task.add_task("Subtask to delete")
        
        # Verify the subtasks were added correctly
        self.assertIsNotNone(parent_task.subtasks)
        assert parent_task.subtasks is not None  # For Pylance
        self.assertEqual(len(parent_task.subtasks.tasks), 2)
        self.assertEqual(parent_task.subtasks.tasks[0].description, "Subtask to keep")
        self.assertEqual(parent_task.subtasks.tasks[1].description, "Subtask to delete")
        
        # Get the IDs
        parent_id = parent_task.get_id()
        subtask1_id = subtask1.get_id("1")
        subtask2_id = subtask2.get_id("1")
        
        # Delete the second subtask
        success = task_list.delete(subtask2_id)
        
        # Verify the deletion was successful
        self.assertTrue(success)
        self.assertIsNotNone(parent_task.subtasks)
        assert parent_task.subtasks is not None  # For Pylance
        self.assertEqual(len(parent_task.subtasks.tasks), 1)
        self.assertEqual(parent_task.subtasks.tasks[0].description, "Subtask to keep")
        
        # Verify the subtask is no longer in the task list
        self.assertIsNone(task_list.get_task_by_id(subtask2_id))


if __name__ == "__main__":
    unittest.main()