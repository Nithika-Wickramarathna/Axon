"""
Advanced Business Logic for Axon Intelligence
Includes AI features, intelligent filtering, and complete management
"""

from typing import List, Optional, Tuple
from models import Thought, Category, Priority, Status, Analytics
from storage import StorageManager
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import re


class ThoughtManager:
    """Advanced thought manager with AI features"""
    
    # Priority keywords
    PRIORITY_KEYWORDS = {
        'high': ['urgent', 'asap', 'critical', 'must', 'emergency', 'immediately', 'today'],
        'medium': ['soon', 'important', 'should', 'need'],
        'low': ['later', 'maybe', 'eventually', 'someday', 'consider']
    }
    
    # Category keywords
    CATEGORY_KEYWORDS = {
        'task': ['need', 'must', 'should', 'do', 'finish', 'complete', 'deadline', 'due', 'schedule'],
        'idea': ['maybe', 'could', 'might', 'what if', 'imagine', 'think', 'create', 'build', 'explore'],
        'worry': ['stressed', 'worried', 'anxious', 'afraid', 'scared', 'concerned', 'nervous', 'doubt']
    }
    
    def __init__(self, storage: StorageManager):
        """Initialize with storage backend"""
        self.storage = storage
    
    # ========== CORE CRUD OPERATIONS ==========
    
    def create_thought(self, text: str, category: Optional[Category] = None, 
                      priority: Optional[Priority] = None) -> Tuple[bool, str, Optional[Thought]]:
        """
        Create a new thought with AI-powered suggestions
        
        Args:
            text: Thought text
            category: Optional override for auto-detected category
            priority: Optional override for auto-detected priority
        
        Returns:
            (success, message, thought)
        """
        try:
            # Validate
            if not text or not text.strip():
                return False, "Thought cannot be empty", None
            
            text = text.strip()
            
            # Check duplicates
            dup_score, dup_thought = self.detect_duplicate(text)
            if dup_score > 0.85:
                return False, f"Similar thought already exists (match: {dup_score:.0%})", None
            
            # Auto-detect if not provided
            if category is None:
                category = self._auto_detect_category(text)
            
            if priority is None:
                priority = self._auto_detect_priority(text)
            
            # Get confidence scores
            category_confidence = self._get_confidence(text, category)
            priority_confidence = self._get_confidence(text, priority)
            avg_confidence = (category_confidence + priority_confidence) / 2
            
            # Create thought
            thought = Thought(
                text=text,
                category=category,
                priority=priority,
                confidence=round(avg_confidence, 2)
            )
            
            # Save
            if self.storage.add(thought):
                return True, f"✓ Created {category.value}", thought
            
            return False, "Failed to save thought", None
        
        except Exception as e:
            return False, f"Error: {str(e)}", None
    
    def delete_thought(self, thought_id: str, permanent: bool = False) -> Tuple[bool, str]:
        """
        Delete thought (soft or permanent)
        
        Args:
            thought_id: ID of thought to delete
            permanent: If True, permanently delete. If False, soft delete (archive)
        
        Returns:
            (success, message)
        """
        thought = self.storage.get_by_id(thought_id)
        if not thought:
            return False, "Thought not found"
        
        if permanent:
            if self.storage.delete(thought_id):
                return True, "✓ Permanently deleted"
        else:
            thought.soft_delete()
            if self.storage.update(thought_id, thought):
                return True, "✓ Archived (can be restored)"
        
        return False, "Failed to delete"
    
    def restore_thought(self, thought_id: str) -> Tuple[bool, str]:
        """Restore a soft-deleted thought"""
        thought = self.storage.get_by_id(thought_id, include_deleted=True)
        if not thought:
            return False, "Thought not found"
        
        if not thought.is_deleted:
            return False, "Thought is not deleted"
        
        thought.restore()
        if self.storage.update(thought_id, thought):
            return True, "✓ Restored"
        
        return False, "Failed to restore"
    
    def toggle_complete(self, thought_id: str) -> Tuple[bool, str]:
        """Toggle completion status"""
        thought = self.storage.get_by_id(thought_id)
        if not thought:
            return False, "Thought not found"
        
        if thought.status == Status.COMPLETED:
            thought.mark_incomplete()
            status_str = "incomplete"
        else:
            thought.mark_complete()
            status_str = "completed"
        
        if self.storage.update(thought_id, thought):
            return True, f"✓ Marked {status_str}"
        
        return False, "Failed to update"
    
    # ========== UNIFIED FILTERING & SORTING ==========
    
    def get_thoughts(self, search: Optional[str] = None, category: Optional[Category] = None,
                    priority: Optional[Priority] = None, completed: Optional[bool] = None,
                    sort_by: str = "priority_date", include_archived: bool = False) -> List[Thought]:
        """
        Get thoughts with unified filtering and sorting
        
        Args:
            search: Search by text keyword
            category: Filter by category
            priority: Filter by priority
            completed: Filter by completion status (True/False/None=all)
            sort_by: "priority_date", "date", "newest", "oldest", "priority", "name"
            include_archived: Include archived thoughts
        
        Returns:
            Filtered and sorted list of thoughts
        """
        thoughts = self.storage.load()
        
        # Remove deleted (but keep archived if requested)
        thoughts = [t for t in thoughts if not t.is_deleted]
        
        # Filter by archive status
        if not include_archived:
            thoughts = [t for t in thoughts if not t.is_archived]
        
        # Apply filters
        if search:
            search_lower = search.lower()
            thoughts = [t for t in thoughts if search_lower in t.text.lower()]
        
        if category:
            thoughts = [t for t in thoughts if t.category == category]
        
        if priority:
            thoughts = [t for t in thoughts if t.priority == priority]
        
        if completed is not None:
            status = Status.COMPLETED if completed else Status.ACTIVE
            thoughts = [t for t in thoughts if (t.status == status) == completed]
        
        # Apply sorting
        if sort_by == "priority_date":
            priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
            thoughts.sort(key=lambda t: (priority_order.get(t.priority, 3), t.created_at), reverse=True)
        elif sort_by == "priority":
            priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
            thoughts.sort(key=lambda t: priority_order.get(t.priority, 3))
        elif sort_by == "date" or sort_by == "newest":
            thoughts.sort(key=lambda t: t.created_at, reverse=True)
        elif sort_by == "oldest":
            thoughts.sort(key=lambda t: t.created_at)
        elif sort_by == "name":
            thoughts.sort(key=lambda t: t.text)
        
        return thoughts
    
    # ========== AI FEATURES ==========
    
    def _auto_detect_priority(self, text: str) -> Priority:
        """Auto-detect priority from text"""
        text_lower = text.lower()
        
        for priority_level, keywords in self.PRIORITY_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                return Priority(priority_level)
        
        return Priority.MEDIUM
    
    def _auto_detect_category(self, text: str) -> Category:
        """Auto-detect category from text"""
        text_lower = text.lower()
        scores = {}
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[category] = score
        
        # Find category with highest score
        best_category = max(scores, key=scores.get)
        return Category(best_category) if scores[best_category] > 0 else Category.IDEA
    
    def _get_confidence(self, text: str, detected_type) -> float:
        """Get confidence score for AI detection"""
        text_lower = text.lower()
        keywords = []
        
        if isinstance(detected_type, Priority):
            keywords = self.PRIORITY_KEYWORDS.get(detected_type.value, [])
        elif isinstance(detected_type, Category):
            keywords = self.CATEGORY_KEYWORDS.get(detected_type.value, [])
        
        if not keywords:
            return 0.5
        
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        confidence = min(0.95, 0.5 + (matches * 0.15))
        return confidence
    
    def detect_duplicate(self, text: str, threshold: float = 0.75) -> Tuple[float, Optional[Thought]]:
        """
        Detect duplicate using similarity score
        
        Args:
            text: Text to check
            threshold: Similarity threshold (0-1)
        
        Returns:
            (similarity_score, matching_thought or None)
        """
        thoughts = self.storage.load()
        best_match = 0.0
        best_thought = None
        
        for thought in thoughts:
            if thought.is_deleted:
                continue
            
            similarity = SequenceMatcher(None, text.lower(), thought.text.lower()).ratio()
            
            if similarity > best_match:
                best_match = similarity
                best_thought = thought
        
        if best_match >= threshold:
            return best_match, best_thought
        
        return best_match, None
    
    # ========== ANALYTICS ==========
    
    def get_analytics(self) -> Analytics:
        """Get comprehensive analytics"""
        thoughts = self.storage.load()
        active_thoughts = [t for t in thoughts if not t.is_deleted and not t.is_archived]
        
        if not thoughts:
            return Analytics()
        
        # Count statistics
        total = len([t for t in thoughts if not t.is_deleted])
        completed = len([t for t in thoughts if t.status == Status.COMPLETED and not t.is_deleted])
        archived = len([t for t in thoughts if t.is_archived])
        active = len(active_thoughts)
        
        # By category
        by_category = {}
        for cat in Category:
            count = len([t for t in active_thoughts if t.category == cat])
            if count > 0:
                by_category[cat.value] = count
        
        # By priority
        by_priority = {}
        for pri in Priority:
            count = len([t for t in active_thoughts if t.priority == pri])
            if count > 0:
                by_priority[pri.value] = count
        
        # Completion rate
        completion_rate = (completed / total * 100) if total > 0 else 0.0
        
        # Weekly trend
        weekly_trend = self._get_weekly_trend(active_thoughts)
        
        # Average confidence
        avg_confidence = sum(t.confidence for t in active_thoughts) / len(active_thoughts) if active_thoughts else 0.0
        
        return Analytics(
            total_thoughts=total,
            completed_thoughts=completed,
            archived_thoughts=archived,
            active_thoughts=active,
            by_category=by_category,
            by_priority=by_priority,
            completion_rate=round(completion_rate, 1),
            weekly_trend=weekly_trend,
            avg_confidence=round(avg_confidence, 2)
        )
    
    def _get_weekly_trend(self, thoughts: List[Thought]) -> List[int]:
        """Get daily activity for last 7 days"""
        trend = [0] * 7
        now = datetime.now()
        
        for thought in thoughts:
            created = datetime.fromisoformat(thought.created_at)
            days_ago = (now - created).days
            
            if 0 <= days_ago < 7:
                trend[6 - days_ago] += 1
        
        return trend
    
    def get_all(self) -> List[Thought]:
        """Get all active thoughts"""
        return self.get_thoughts()
    
    def export_csv(self) -> str:
        """Export thoughts as CSV"""
        thoughts = self.storage.load()
        
        if not thoughts:
            return ""
        
        csv_lines = ["id,text,category,priority,status,created_at"]
        
        for thought in thoughts:
            if not thought.is_deleted:
                csv_lines.append(
                    f'{thought.id},'
                    f'"{thought.text}",'
                    f'{thought.category.value},'
                    f'{thought.priority.value},'
                    f'{thought.status.value},'
                    f'{thought.created_at}'
                )
        
        return '\n'.join(csv_lines)