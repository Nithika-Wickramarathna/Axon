"""
Storage layer for Axon Intelligence
Handles JSON persistence with soft delete and archive support
"""

import json
import os
from typing import List, Optional
from models import Thought


class StorageManager:
    """Manages data persistence"""
    
    def __init__(self, filename: str = "axon_thoughts.json"):
        """Initialize storage"""
        self.filename = filename
        self._ensure_db()
    
    def _ensure_db(self):
        """Ensure database file exists"""
        if not os.path.exists(self.filename):
            self.save([])
    
    def load(self, include_deleted: bool = False) -> List[Thought]:
        """Load all thoughts"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    thoughts = [Thought.from_dict(item) for item in data]
                    
                    if not include_deleted:
                        thoughts = [t for t in thoughts if not t.is_deleted]
                    
                    return thoughts
        except Exception as e:
            print(f"Error loading: {e}")
        
        return []
    
    def save(self, thoughts: List[Thought]) -> bool:
        """Save all thoughts"""
        try:
            with open(self.filename, 'w') as f:
                data = [thought.to_dict() for thought in thoughts]
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving: {e}")
            return False
    
    def add(self, thought: Thought) -> bool:
        """Add a thought"""
        try:
            thoughts = self.load(include_deleted=True)
            thoughts.append(thought)
            return self.save(thoughts)
        except Exception as e:
            print(f"Error adding: {e}")
            return False
    
    def update(self, thought_id: str, thought: Thought) -> bool:
        """Update a thought"""
        try:
            thoughts = self.load(include_deleted=True)
            for i, t in enumerate(thoughts):
                if t.id == thought_id:
                    thoughts[i] = thought
                    return self.save(thoughts)
            return False
        except Exception as e:
            print(f"Error updating: {e}")
            return False
    
    def delete(self, thought_id: str) -> bool:
        """Permanently delete a thought"""
        try:
            thoughts = self.load(include_deleted=True)
            thoughts = [t for t in thoughts if t.id != thought_id]
            return self.save(thoughts)
        except Exception as e:
            print(f"Error deleting: {e}")
            return False
    
    def get_by_id(self, thought_id: str, include_deleted: bool = False) -> Optional[Thought]:
        """Get a specific thought"""
        thoughts = self.load(include_deleted=include_deleted)
        for t in thoughts:
            if t.id == thought_id:
                return t
        return None
    
    def export_csv(self) -> str:
        """Export as CSV"""
        thoughts = self.load()
        
        if not thoughts:
            return ""
        
        csv_lines = ["id,text,category,priority,status,created_at"]
        
        for thought in thoughts:
            csv_lines.append(
                f'{thought.id},'
                f'"{thought.text}",'
                f'{thought.category.value},'
                f'{thought.priority.value},'
                f'{thought.status.value},'
                f'{thought.created_at}'
            )
        
        return '\n'.join(csv_lines)