"""
Unit tests for Axon Intelligence business logic
Tests all core functions and AI features
"""

import unittest
from models import Thought, Category, Priority, Status
from storage import StorageManager
from logic import ThoughtManager
import os


class TestThoughtModel(unittest.TestCase):
    """Test data model"""
    
    def test_thought_creation(self):
        """Test creating a thought"""
        thought = Thought(text="Test thought", category=Category.TASK)
        self.assertEqual(thought.text, "Test thought")
        self.assertEqual(thought.category, Category.TASK)
        self.assertIsNotNone(thought.id)
    
    def test_thought_validation(self):
        """Test thought validation"""
        with self.assertRaises(ValueError):
            Thought(text="", category=Category.TASK)
        
        with self.assertRaises(ValueError):
            Thought(text="ab", category=Category.TASK)
    
    def test_soft_delete(self):
        """Test soft delete"""
        thought = Thought(text="Test", category=Category.TASK)
        thought.soft_delete()
        self.assertTrue(thought.is_deleted)
        self.assertIsNotNone(thought.deleted_at)
    
    def test_archive(self):
        """Test archive"""
        thought = Thought(text="Test", category=Category.TASK)
        thought.archive()
        self.assertTrue(thought.is_archived)
        self.assertEqual(thought.status, Status.ARCHIVED)


class TestThoughtManager(unittest.TestCase):
    """Test business logic"""
    
    def setUp(self):
        """Setup test storage"""
        self.storage_file = "test_thoughts.json"
        self.storage = StorageManager(self.storage_file)
        self.manager = ThoughtManager(self.storage)
    
    def tearDown(self):
        """Cleanup"""
        if os.path.exists(self.storage_file):
            os.remove(self.storage_file)
    
    def test_create_thought(self):
        """Test creating a thought"""
        success, message, thought = self.manager.create_thought("Test task", Category.TASK)
        self.assertTrue(success)
        self.assertIsNotNone(thought)
        self.assertEqual(thought.text, "Test task")
    
    def test_auto_detect_priority(self):
        """Test auto-priority detection"""
        # High priority
        priority = self.manager._auto_detect_priority("This is urgent!")
        self.assertEqual(priority, Priority.HIGH)
        
        # Low priority
        priority = self.manager._auto_detect_priority("Maybe later")
        self.assertEqual(priority, Priority.LOW)
        
        # Default
        priority = self.manager._auto_detect_priority("Random thought")
        self.assertEqual(priority, Priority.MEDIUM)
    
    def test_auto_detect_category(self):
        """Test auto-category detection"""
        # Task
        category = self.manager._auto_detect_category("I need to finish this")
        self.assertEqual(category, Category.TASK)
        
        # Worry
        category = self.manager._auto_detect_category("I'm worried about this")
        self.assertEqual(category, Category.WORRY)
        
        # Idea
        category = self.manager._auto_detect_category("Maybe I could try this")
        self.assertEqual(category, Category.IDEA)
    
    def test_duplicate_detection(self):
        """Test duplicate detection"""
        # Create first thought
        self.manager.create_thought("This is a test", Category.TASK)
        
        # Try to create similar
        similarity, dup = self.manager.detect_duplicate("This is a test")
        self.assertGreater(similarity, 0.9)
        self.assertIsNotNone(dup)
    
    def test_get_thoughts_filtering(self):
        """Test unified filtering"""
        # Create test thoughts
        self.manager.create_thought("Task 1", Category.TASK, Priority.HIGH)
        self.manager.create_thought("Idea 1", Category.IDEA, Priority.MEDIUM)
        self.manager.create_thought("Worry 1", Category.WORRY, Priority.LOW)
        
        # Test filtering by category
        tasks = self.manager.get_thoughts(category=Category.TASK)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].category, Category.TASK)
        
        # Test filtering by priority
        high = self.manager.get_thoughts(priority=Priority.HIGH)
        self.assertEqual(len(high), 1)
        self.assertEqual(high[0].priority, Priority.HIGH)
        
        # Test search
        results = self.manager.get_thoughts(search="Task")
        self.assertEqual(len(results), 1)
    
    def test_toggle_complete(self):
        """Test completion toggle"""
        success, message, thought = self.manager.create_thought("Test", Category.TASK)
        
        # Mark complete
        success, msg = self.manager.toggle_complete(thought.id)
        self.assertTrue(success)
        
        # Verify
        updated = self.storage.get_by_id(thought.id)
        self.assertEqual(updated.status, Status.COMPLETED)
    
    def test_delete_thought(self):
        """Test soft delete"""
        success, message, thought = self.manager.create_thought("Test", Category.TASK)
        
        # Delete
        success, msg = self.manager.delete_thought(thought.id)
        self.assertTrue(success)
        
        # Verify soft delete
        deleted = self.storage.get_by_id(thought.id, include_deleted=True)
        self.assertTrue(deleted.is_deleted)
    
    def test_analytics(self):
        """Test analytics calculation"""
        # Create various thoughts
        self.manager.create_thought("Task", Category.TASK)
        self.manager.create_thought("Idea", Category.IDEA)
        self.manager.create_thought("Worry", Category.WORRY)
        
        # Get analytics
        analytics = self.manager.get_analytics()
        
        self.assertEqual(analytics.total_thoughts, 3)
        self.assertEqual(analytics.active_thoughts, 3)
        self.assertEqual(len(analytics.by_category), 3)


if __name__ == '__main__':
    unittest.main()

