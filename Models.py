"""
Data models for Axon Intelligence
Defines the structure of thoughts and enums
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from uuid import uuid4
from typing import Optional


class Category(str, Enum):
    """Thought categories"""
    TASK = "task"
    IDEA = "idea"
    WORRY = "worry"


class Priority(str, Enum):
    """Priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Thought:
    """Thought data model"""
    text: str
    category: Category
    priority: Priority = Priority.MEDIUM
    completed: bool = False
    id: str = None
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        """Initialize auto-generated fields"""
        if self.id is None:
            self.id = str(uuid4())
        
        now = datetime.now().isoformat()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'text': self.text,
            'category': self.category.value,
            'priority': self.priority.value,
            'completed': self.completed,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Thought':
        """Create from dictionary"""
        return cls(
            text=data['text'],
            category=Category(data['category']),
            priority=Priority(data['priority']),
            completed=data.get('completed', False),
            id=data.get('id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def mark_complete(self):
        """Mark thought as completed"""
        self.completed = True
        self.updated_at = datetime.now().isoformat()
    
    def mark_incomplete(self):
        """Mark thought as incomplete"""
        self.completed = False
        self.updated_at = datetime.now().isoformat()