"""
Business logic for Axon Intelligence
Core operations for thought management
"""

from typing import List, Optional
from models import Thought, Category, Priority
from storage import StorageManager
from datetime import datetime


class ThoughtManager:
    """Manages thought operations"""
    
    def __init__(self, storage: StorageManager):
        """Initialize thought manager"""
        self.storage = storage
    
    def create_thought(self, text: str, category: Category, 
                      priority: Priority = Priority.MEDIUM) -> tuple[bool, str]:
        """
        Create a new thought
        
        Args:
            text: Thought text
            category: Category enum
            priority: Priority enum
        
        Returns:
            (success: bool, message: str)
        """
        # Validate
        if not text or not text.strip():
            return False, "Thought cannot be empty"
        
        text = text.strip()
        
        # Check for duplicates
        if self._is_duplicate(text):
            return False, "Similar thought already exists"
        
        if len(text) < 3:
            return False, "Thought must be at least 3 characters"
        
        if len(text) > 5000:
            return False, "Thought must be less than 5000 characters"
        
        # Create and save
        thought = Thought(
            text=text,
            category=category,
            priority=priority
        )
        
        if self.storage.add(thought):
            return True, f"✓ Created {category.value}"
        
        return False, "Failed to save thought"
    
    def delete_thought(self, thought_id: str) -> tuple[bool, str]:
        """Delete a thought"""
        if self.storage.delete(thought_id):
            return True, "✓ Deleted"
        return False, "Failed to delete"
    
    def toggle_complete(self, thought_id: str) -> tuple[bool, str]:
        """Toggle thought completion status"""
        thought = self.storage.get_by_id(thought_id)
        
        if not thought:
            return False, "Thought not found"
        
        if thought.completed:
            thought.mark_incomplete()
        else:
            thought.mark_complete()
        
        if self.storage.update(thought_id, thought):
            status = "completed" if thought.completed else "incomplete"
            return True, f"✓ Marked as {status}"
        
        return False, "Failed to update"
    
    def get_all(self) -> List[Thought]:
        """Get all thoughts"""
        return self.storage.load()
    
    def search(self, query: str) -> List[Thought]:
        """Search thoughts by keyword"""
        if not query or not query.strip():
            return self.get_all()
        
        query_lower = query.lower().strip()
        thoughts = self.get_all()
        
        return [t for t in thoughts if query_lower in t.text.lower()]
    
    def filter_by_category(self, category: Category) -> List[Thought]:
        """Filter thoughts by category"""
        thoughts = self.get_all()
        return [t for t in thoughts if t.category == category]
    
    def filter_by_priority(self, priority: Priority) -> List[Thought]:
        """Filter thoughts by priority"""
        thoughts = self.get_all()
        return [t for t in thoughts if t.priority == priority]
    
    def filter_by_status(self, completed: bool) -> List[Thought]:
        """Filter thoughts by completion status"""
        thoughts = self.get_all()
        return [t for t in thoughts if t.completed == completed]
    
    def sort_by_priority(self, thoughts: List[Thought]) -> List[Thought]:
        """Sort thoughts by priority (high → medium → low)"""
        priority_order = {
            Priority.HIGH: 0,
            Priority.MEDIUM: 1,
            Priority.LOW: 2
        }
        
        return sorted(thoughts, key=lambda t: priority_order.get(t.priority, 3))
    
    def sort_by_date(self, thoughts: List[Thought], newest_first: bool = True) -> List[Thought]:
        """Sort thoughts by date"""
        return sorted(
            thoughts,
            key=lambda t: t.created_at,
            reverse=newest_first
        )
    
    def get_stats(self) -> dict:
        """Get statistics about thoughts"""
        thoughts = self.get_all()
        
        if not thoughts:
            return {
                'total': 0,
                'completed': 0,
                'pending': 0,
                'by_category': {},
                'by_priority': {}
            }
        
        by_category = {}
        by_priority = {}
        completed_count = 0
        
        for thought in thoughts:
            # Count by category
            cat = thought.category.value
            by_category[cat] = by_category.get(cat, 0) + 1
            
            # Count by priority
            pri = thought.priority.value
            by_priority[pri] = by_priority.get(pri, 0) + 1
            
            # Count completed
            if thought.completed:
                completed_count += 1
        
        return {
            'total': len(thoughts),
            'completed': completed_count,
            'pending': len(thoughts) - completed_count,
            'by_category': by_category,
            'by_priority': by_priority,
            'completion_rate': round((completed_count / len(thoughts)) * 100, 1) if thoughts else 0
        }
    
    def _is_duplicate(self, text: str, threshold: float = 0.85) -> bool:
        """Check if thought is a duplicate (simple check)"""
        text_lower = text.lower().strip()
        thoughts = self.get_all()
        
        for thought in thoughts:
            thought_lower = thought.text.lower().strip()
            
            # Exact match
            if text_lower == thought_lower:
                return True
            
            # Contains check (if text is very similar)
            if len(text_lower) > 10 and len(thought_lower) > 10:
                # Simple substring check
                if text_lower in thought_lower or thought_lower in text_lower:
                    return True
        
        return False
    
    def export_csv(self) -> str:
        """Export all thoughts as CSV"""
        return self.storage.export_csv()