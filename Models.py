"""
Advanced Data Models for Axon Intelligence
Includes all enums, validations, and data structures
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from uuid import uuid4
from typing import Optional, List
import hashlib


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


class Status(str, Enum):
    """Thought status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class Thought:
    """Advanced thought data model with full integrity support"""
    
    text: str
    category: Category
    priority: Priority = Priority.MEDIUM
    status: Status = Status.ACTIVE
    
    # Auto-generated fields
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Optional fields
    tags: List[str] = field(default_factory=list)
    confidence: float = 0.8  # For AI suggestions
    is_archived: bool = False
    is_deleted: bool = False  # Soft delete flag
    deleted_at: Optional[str] = None
    
    def __post_init__(self):
        """Validate on creation"""
        if not self.text or not self.text.strip():
            raise ValueError("Thought text cannot be empty")
        if len(self.text.strip()) < 3:
            raise ValueError("Thought must be at least 3 characters")
        if len(self.text) > 5000:
            raise ValueError("Thought must be less than 5000 characters")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'id': self.id,
            'text': self.text,
            'category': self.category.value,
            'priority': self.priority.value,
            'status': self.status.value,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'tags': self.tags,
            'confidence': self.confidence,
            'is_archived': self.is_archived,
            'is_deleted': self.is_deleted,
            'deleted_at': self.deleted_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Thought':
        """Create from dictionary"""
        return cls(
            text=data['text'],
            category=Category(data['category']),
            priority=Priority(data['priority']),
            status=Status(data.get('status', 'active')),
            id=data.get('id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            tags=data.get('tags', []),
            confidence=data.get('confidence', 0.8),
            is_archived=data.get('is_archived', False),
            is_deleted=data.get('is_deleted', False),
            deleted_at=data.get('deleted_at')
        )
    
    def soft_delete(self):
        """Soft delete: mark as deleted but keep data"""
        self.is_deleted = True
        self.deleted_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def restore(self):
        """Restore soft-deleted thought"""
        self.is_deleted = False
        self.deleted_at = None
        self.updated_at = datetime.now().isoformat()
    
    def archive(self):
        """Archive thought"""
        self.is_archived = True
        self.status = Status.ARCHIVED
        self.updated_at = datetime.now().isoformat()
    
    def unarchive(self):
        """Unarchive thought"""
        self.is_archived = False
        self.status = Status.ACTIVE
        self.updated_at = datetime.now().isoformat()
    
    def mark_complete(self):
        """Mark as completed"""
        self.status = Status.COMPLETED
        self.updated_at = datetime.now().isoformat()
    
    def mark_incomplete(self):
        """Mark as incomplete"""
        self.status = Status.ACTIVE
        self.updated_at = datetime.now().isoformat()
    
    def get_hash(self) -> str:
        """Get SHA256 hash of thought text for duplicate detection"""
        return hashlib.sha256(self.text.lower().encode()).hexdigest()


@dataclass
class Analytics:
    """Analytics data structure"""
    total_thoughts: int = 0
    completed_thoughts: int = 0
    archived_thoughts: int = 0
    active_thoughts: int = 0
    by_category: dict = field(default_factory=dict)
    by_priority: dict = field(default_factory=dict)
    completion_rate: float = 0.0
    weekly_trend: list = field(default_factory=list)
    avg_confidence: float = 0.0