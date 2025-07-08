"""Unit tests for the Task model."""
import unittest
from pathlib import Path
from typing import cast

from mcp_todo.models import Task, TaskList, TaskState


class TestTaskModel(unittest.TestCase):
    """Test cases for the Task model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.task_list = TaskList()
        self.task = Task(description="Test task")
    
    def test_task_initialization(self):
        """Test that a task is initialized with the correct default values."""
        self.assertEqual(self.task.description, "Test task")
        self.assertEqual(self.task.state, TaskState.PENDING)
        self.assertIsNone(self.task.parent)
        self.assertIsNotNone(self.task.subtasks)
        self.assertIsInstance(self.task.subtasks, TaskList)
        
        # Use cast to help Pylance understand that subtasks is not None
        task_subtasks = cast(TaskList, self.task.subtasks)
        self.assertEqual(len(task_subtasks.tasks), 0)
    
    def test_task_id_generation(self):
        """Test that task IDs are generated correctly."""
        # Add tasks to the task list
        task1 = self.task_list.add_task("Task 1")
        task2 = self.task_list.add_task("Task 2")
        
        # Check top-level task IDs
        self.assertEqual(task1.get_id(), "1")
        self.assertEqual(task2.get_id(), "2")
        
        # Add subtasks
        # Use cast to help Pylance understand that subtasks is not None
        task_list1 = cast(TaskList, task1.subtasks)
        subtask1 = task_list1.add_task("Subtask 1.1")
        subtask2 = task_list1.add_task("Subtask 1.2")
        
        # Check subtask IDs
        self.assertEqual(subtask1.get_id("1"), "1.1")
        self.assertEqual(subtask2.get_id("1"), "1.2")
        
        # Add sub-subtasks
        # Use cast to help Pylance understand that subtasks is not None
        subtask_list = cast(TaskList, subtask1.subtasks)
        subsubtask = subtask_list.add_task("Subsubtask 1.1.1")
        
        # Check sub-subtask IDs
        self.assertEqual(subsubtask.get_id("1.1"), "1.1.1")
    
    def test_to_markdown(self):
        """Test that tasks are correctly converted to markdown."""
        # Create a task with subtasks
        task = self.task_list.add_task("Main task")
        
        # Use cast to help Pylance understand that subtasks is not None
        task_subtasks = cast(TaskList, task.subtasks)
        subtask1 = task_subtasks.add_task("Subtask 1")
        subtask2 = task_subtasks.add_task("Subtask 2")
        
        # Mark one subtask as completed
        subtask1.state = TaskState.COMPLETED
        
        # Generate markdown
        markdown = task.to_markdown()
        
        # Check that the markdown contains the expected content
        self.assertIn("- [ ] 1: Main task", markdown)
        self.assertIn("- [x] 1.1: Subtask 1", markdown)
        self.assertIn("- [ ] 1.2: Subtask 2", markdown)
        
    def test_task_equality(self):
        """Test that tasks are compared correctly for equality."""
        # Create two identical tasks
        task1 = Task(description="Test task")
        task2 = Task(description="Test task")
        
        # They should be equal
        self.assertEqual(task1, task2)
        
        # Change state of one task
        task2.state = TaskState.COMPLETED
        self.assertNotEqual(task1, task2)
        
        # Reset state and add different subtasks
        task2.state = TaskState.PENDING
        task1.add_task("Subtask 1")
        self.assertNotEqual(task1, task2)
        
        # Make subtasks identical
        task2.add_task("Subtask 1")
        self.assertEqual(task1, task2)
        
        # Test that parent references don't cause infinite recursion
        task_list = TaskList()
        task3 = task_list.add_task("Parent task")
        task3.add_task("Subtask 1")  # Add the same subtask to task3
        task4 = Task(description="Parent task")
        task4.add_task("Subtask 1")  # Same structure as task3
        
        # Even though task3 has a parent and task4 doesn't, they should be equal
        # because we're ignoring parent references in equality comparison
        self.assertEqual(task3, task4)


if __name__ == "__main__":
    unittest.main()