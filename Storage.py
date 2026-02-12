"""
Storage layer for Axon Intelligence
Handles JSON persistence and data operations
"""

import json
import os
from typing import List
from models import Thought


class StorageManager:
    """Handles all data persistence"""
    
    def __init__(self, filename: str = "axon_thoughts.json"):
        """Initialize storage manager"""
        self.filename = filename
    
    def load(self) -> List[Thought]:
        """Load all thoughts from storage"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    return [Thought.from_dict(item) for item in data]
        except Exception as e:
            print(f"Error loading thoughts: {e}")
        
        return []
    
    def save(self, thoughts: List[Thought]) -> bool:
        """Save all thoughts to storage"""
        try:
            with open(self.filename, 'w') as f:
                data = [thought.to_dict() for thought in thoughts]
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving thoughts: {e}")
            return False
    
    def add(self, thought: Thought) -> bool:
        """Add a new thought"""
        try:
            thoughts = self.load()
            thoughts.append(thought)
            return self.save(thoughts)
        except Exception as e:
            print(f"Error adding thought: {e}")
            return False
    
    def update(self, thought_id: str, thought: Thought) -> bool:
        """Update an existing thought"""
        try:
            thoughts = self.load()
            for i, t in enumerate(thoughts):
                if t.id == thought_id:
                    thoughts[i] = thought
                    return self.save(thoughts)
            return False
        except Exception as e:
            print(f"Error updating thought: {e}")
            return False
    
    def delete(self, thought_id: str) -> bool:
        """Delete a thought"""
        try:
            thoughts = self.load()
            thoughts = [t for t in thoughts if t.id != thought_id]
            return self.save(thoughts)
        except Exception as e:
            print(f"Error deleting thought: {e}")
            return False
    
    def get_by_id(self, thought_id: str) -> Thought:
        """Get a specific thought by ID"""
        thoughts = self.load()
        for t in thoughts:
            if t.id == thought_id:
                return t
        return None
    
    def export_csv(self) -> str:
        """Export thoughts as CSV"""
        try:
            thoughts = self.load()
            
            if not thoughts:
                return ""
            
            csv_lines = ["id,text,category,priority,completed,created_at"]
            
            for thought in thoughts:
                csv_lines.append(
                    f'{thought.id},'
                    f'"{thought.text}",'
                    f'{thought.category.value},'
                    f'{thought.priority.value},'
                    f'{thought.completed},'
                    f'{thought.created_at}'
                )
            
            return '\n'.join(csv_lines)
        
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return ""