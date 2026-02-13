#!/usr/bin/env python3
"""
Axon Intelligence - Production-Ready Application
SaaS-style interface with professional design
FIXED VERSION v2 - All code in one file, all bugs fixed
"""

import streamlit as st
import json
import os
from datetime import datetime
from collections import Counter, defaultdict
from enum import Enum
from uuid import uuid4
from dataclasses import dataclass, asdict


# ============================================================================
# DATA MODELS (from models.py)
# ============================================================================

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


# ============================================================================
# STORAGE MANAGER (from storage.py)
# ============================================================================

class StorageManager:
    """Handles all data persistence"""
    
    def __init__(self, filename: str = "axon_thoughts.json"):
        """Initialize storage manager"""
        self.filename = filename
    
    def load(self):
        """Load all thoughts from storage"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    return [Thought.from_dict(item) for item in data]
        except Exception as e:
            print(f"Error loading thoughts: {e}")
        
        return []
    
    def save(self, thoughts) -> bool:
        """Save all thoughts to storage"""
        try:
            with open(self.filename, 'w') as f:
                data = [thought.to_dict() for thought in thoughts]
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving thoughts: {e}")
            return False
    
    def add(self, thought) -> bool:
        """Add a new thought"""
        try:
            thoughts = self.load()
            thoughts.append(thought)
            return self.save(thoughts)
        except Exception as e:
            print(f"Error adding thought: {e}")
            return False
    
    def update(self, thought_id: str, thought) -> bool:
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
    
    def get_by_id(self, thought_id: str):
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


# ============================================================================
# THOUGHT MANAGER (from logic.py)
# ============================================================================

class ThoughtManager:
    """Manages thought operations"""
    
    def __init__(self, storage):
        """Initialize thought manager"""
        self.storage = storage
    
    def create_thought(self, text: str, category: Category, 
                      priority: Priority = Priority.MEDIUM):
        """Create a new thought"""
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
    
    def delete_thought(self, thought_id: str):
        """Delete a thought"""
        if self.storage.delete(thought_id):
            return True, "✓ Deleted"
        return False, "Failed to delete"
    
    def toggle_complete(self, thought_id: str):
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
    
    def get_all(self):
        """Get all thoughts"""
        return self.storage.load()
    
    def search(self, query: str):
        """Search thoughts by keyword"""
        if not query or not query.strip():
            return self.get_all()
        
        query_lower = query.lower().strip()
        thoughts = self.get_all()
        
        return [t for t in thoughts if query_lower in t.text.lower()]
    
    def filter_by_category(self, category: Category):
        """Filter thoughts by category"""
        thoughts = self.get_all()
        return [t for t in thoughts if t.category == category]
    
    def filter_by_priority(self, priority: Priority):
        """Filter thoughts by priority"""
        thoughts = self.get_all()
        return [t for t in thoughts if t.priority == priority]
    
    def filter_by_status(self, completed: bool):
        """Filter thoughts by completion status"""
        thoughts = self.get_all()
        return [t for t in thoughts if t.completed == completed]
    
    def sort_by_priority(self, thoughts):
        """Sort thoughts by priority (high → medium → low)"""
        priority_order = {
            Priority.HIGH: 0,
            Priority.MEDIUM: 1,
            Priority.LOW: 2
        }
        
        return sorted(thoughts, key=lambda t: priority_order.get(t.priority, 3))
    
    def sort_by_date(self, thoughts, newest_first: bool = True):
        """Sort thoughts by date"""
        return sorted(
            thoughts,
            key=lambda t: t.created_at,
            reverse=newest_first
        )
    
    def get_stats(self) -> dict:
        """Get statistics about thoughts - FIXED VERSION"""
        thoughts = self.get_all()
        
        if not thoughts:
            return {
                'total': 0,
                'completed': 0,
                'pending': 0,
                'by_category': {},
                'by_priority': {},
                'completion_rate': 0
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
        
        completion_rate = round((completed_count / len(thoughts)) * 100, 1) if thoughts else 0
        
        return {
            'total': len(thoughts),
            'completed': completed_count,
            'pending': len(thoughts) - completed_count,
            'by_category': by_category,
            'by_priority': by_priority,
            'completion_rate': completion_rate
        }
    
    def _is_duplicate(self, text: str, threshold: float = 0.85) -> bool:
        """Check if thought is a duplicate"""
        text_lower = text.lower().strip()
        thoughts = self.get_all()
        
        for thought in thoughts:
            thought_lower = thought.text.lower().strip()
            
            # Exact match
            if text_lower == thought_lower:
                return True
            
            # Contains check
            if len(text_lower) > 10 and len(thought_lower) > 10:
                if text_lower in thought_lower or thought_lower in text_lower:
                    return True
        
        return False
    
    def export_csv(self) -> str:
        """Export all thoughts as CSV"""
        return self.storage.export_csv()


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Axon Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional SaaS Dark Theme
st.markdown("""
    <style>
    :root {
        --primary: #2563eb;
        --primary-dark: #1e40af;
        --primary-light: #3b82f6;
        --bg-primary: #ffffff;
        --bg-secondary: #f9fafb;
        --text-primary: #111827;
        --text-secondary: #6b7280;
        --border: #e5e7eb;
    }
    
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--bg-secondary);
        color: var(--text-primary);
    }
    
    [data-testid="stSidebar"] {
        background-color: var(--bg-primary);
        border-right: 1px solid var(--border);
    }
    
    .header-container {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        padding: 40px 30px;
        border-radius: 0;
        margin: -50px -50px 30px -50px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0 0 10px 0;
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        opacity: 0.95;
        margin: 0;
        font-weight: 400;
    }
    
    .card {
        background: var(--bg-primary);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        transition: all 0.2s ease;
    }
    
    .card:hover {
        border-color: var(--primary-light);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
    }
    
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .badge-task {
        background-color: #dcfce7;
        color: #166534;
        border: 1px solid #86efac;
    }
    
    .badge-idea {
        background-color: #dbeafe;
        color: #0c4a6e;
        border: 1px solid #93c5fd;
    }
    
    .badge-worry {
        background-color: #fed7aa;
        color: #92400e;
        border: 1px solid #fdba74;
    }
    
    .badge-high {
        background-color: #fee2e2;
        color: #7f1d1d;
    }
    
    .badge-medium {
        background-color: #fef3c7;
        color: #78350f;
    }
    
    .badge-low {
        background-color: #dbeafe;
        color: #0c2d5c;
    }
    
    .stButton > button {
        background: var(--primary);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: var(--primary-dark);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZATION
# ============================================================================

if 'storage' not in st.session_state:
    st.session_state.storage = StorageManager()

if 'manager' not in st.session_state:
    st.session_state.manager = ThoughtManager(st.session_state.storage)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("---")
    st.markdown("### 🧠 Axon")
    st.markdown("*Intelligent thought organization*")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["🏠 Home", "➕ New Thought", "📋 All Thoughts", "📊 Analytics"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    stats = st.session_state.manager.get_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total", stats['total'])
    with col2:
        st.metric("Completed", stats['completed'])
    
    st.markdown("---")
    
    if st.button("📥 Export CSV", use_container_width=True):
        csv_data = st.session_state.manager.export_csv()
        if csv_data:
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"axon_thoughts_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

# ============================================================================
# PAGE: HOME
# ============================================================================

if page == "🏠 Home":
    st.markdown("""
        <div class="header-container">
            <div class="header-title">🧠 Axon Intelligence</div>
            <div class="header-subtitle">Organize your thoughts. Understand your priorities.</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("""
        ### Welcome to Axon
        
        Axon helps you capture and organize your thoughts effortlessly.
        Whether it's a task to complete, an idea to explore, or a worry to process,
        Axon gives you clarity and prioritization.
        
        **Key Features:**
        - 📝 Capture thoughts instantly
        - 🏷️ Categorize (Tasks, Ideas, Worries)
        - ⭐ Prioritize what matters
        - 📊 View analytics and insights
        - 💾 Everything saved locally
        """)
        
        st.markdown("")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.button("➕ New Thought", use_container_width=True, type="primary")
        with col_b:
            st.button("📋 View Thoughts", use_container_width=True)
    
    with col2:
        st.markdown("### Quick Stats")
        
        stats = st.session_state.manager.get_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total", stats['total'])
        with col2:
            st.metric("Completed", stats['completed'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Pending", stats['pending'])
        with col2:
            st.metric("Completion", f"{stats['completion_rate']}%")
    
    st.divider()
    
    st.markdown("### Categories")
    
    stats = st.session_state.manager.get_stats()
    by_category = stats['by_category']
    
    if by_category:
        col1, col2, col3 = st.columns(3)
        
        task_count = by_category.get('task', 0)
        idea_count = by_category.get('idea', 0)
        worry_count = by_category.get('worry', 0)
        
        with col1:
            st.metric("✓ Tasks", task_count)
        with col2:
            st.metric("💡 Ideas", idea_count)
        with col3:
            st.metric("⚠️ Worries", worry_count)
    else:
        st.info("No thoughts yet. Create your first one!")

# ============================================================================
# PAGE: NEW THOUGHT
# ============================================================================

elif page == "➕ New Thought":
    st.markdown("""
        <div class="header-container">
            <div class="header-title">Add a New Thought</div>
            <div class="header-subtitle">Capture what's on your mind</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        thought_text = st.text_area(
            "What's on your mind?",
            placeholder="Type your thought here...",
            height=120,
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("### Details")
        category = st.selectbox(
            "Category",
            [Category.TASK, Category.IDEA, Category.WORRY],
            format_func=lambda x: f"{['✓', '💡', '⚠️'][list(Category).index(x)]} {x.value.capitalize()}"
        )
        
        priority = st.selectbox(
            "Priority",
            [Priority.LOW, Priority.MEDIUM, Priority.HIGH],
            format_func=lambda x: x.value.capitalize()
        )
    
    st.divider()
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("✓ Save Thought", use_container_width=True, type="primary"):
            success, message = st.session_state.manager.create_thought(
                text=thought_text,
                category=category,
                priority=priority
            )
            
            if success:
                st.success(message)
                st.balloons()
            else:
                st.error(message)
    
    with col2:
        if st.button("Clear", use_container_width=True):
            st.rerun()

# ============================================================================
# PAGE: ALL THOUGHTS
# ============================================================================

elif page == "📋 All Thoughts":
    st.markdown("""
        <div class="header-container">
            <div class="header-title">Your Thoughts</div>
            <div class="header-subtitle">Manage and organize your ideas</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        search_query = st.text_input("🔍 Search", placeholder="Search thoughts...")
    
    with col2:
        filter_category = st.selectbox(
            "Category",
            [None] + list(Category),
            format_func=lambda x: "All Categories" if x is None else f"{['✓', '💡', '⚠️'][list(Category).index(x)]} {x.value.capitalize()}"
        )
    
    with col3:
        filter_priority = st.selectbox(
            "Priority",
            [None] + list(Priority),
            format_func=lambda x: "All Priorities" if x is None else x.value.capitalize()
        )
    
    with col4:
        filter_status = st.selectbox(
            "Status",
            ["All", "Pending", "Completed"],
        )
    
    st.divider()
    
    thoughts = st.session_state.manager.get_all()
    
    if search_query:
        thoughts = st.session_state.manager.search(search_query)
    
    if filter_category:
        thoughts = [t for t in thoughts if t.category == filter_category]
    
    if filter_priority:
        thoughts = [t for t in thoughts if t.priority == filter_priority]
    
    if filter_status == "Pending":
        thoughts = [t for t in thoughts if not t.completed]
    elif filter_status == "Completed":
        thoughts = [t for t in thoughts if t.completed]
    
    thoughts = st.session_state.manager.sort_by_priority(thoughts)
    thoughts = st.session_state.manager.sort_by_date(thoughts, newest_first=True)
    
    if not thoughts:
        st.info("No thoughts found.")
    else:
        st.markdown(f"**{len(thoughts)} thought{'s' if len(thoughts) != 1 else ''} found**")
        st.divider()
        
        for thought in thoughts:
            col1, col2 = st.columns([0.1, 0.9])
            
            with col1:
                is_checked = st.checkbox(
                    "",
                    value=thought.completed,
                    key=f"complete_{thought.id}"
                )
                
                if is_checked != thought.completed:
                    st.session_state.manager.toggle_complete(thought.id)
                    st.rerun()
            
            with col2:
                category_emoji = {'task': '✓', 'idea': '💡', 'worry': '⚠️'}
                category_badge = f'<span class="badge badge-{thought.category.value}">{category_emoji[thought.category.value]} {thought.category.value.capitalize()}</span>'
                
                priority_badge = f'<span class="badge badge-{thought.priority.value}">{thought.priority.value.capitalize()}</span>'
                
                st.markdown(f"""
                <div class="card">
                    <div style="margin-bottom: 8px;">
                        {category_badge}
                        {priority_badge}
                    </div>
                    <div style="text-decoration: {'line-through' if thought.completed else 'none'}; opacity: {'0.6' if thought.completed else '1'};">
                        {thought.text}
                    </div>
                    <small style="color: #6b7280;">📅 {thought.created_at[:10]}</small>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🗑️ Delete", key=f"delete_{thought.id}"):
                    st.session_state.manager.delete_thought(thought.id)
                    st.success("Deleted")
                    st.rerun()

# ============================================================================
# PAGE: ANALYTICS
# ============================================================================

elif page == "📊 Analytics":
    st.markdown("""
        <div class="header-container">
            <div class="header-title">Analytics</div>
            <div class="header-subtitle">Insights into your thoughts</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    stats = st.session_state.manager.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Thoughts", stats['total'])
    with col2:
        st.metric("Completed", stats['completed'])
    with col3:
        st.metric("Pending", stats['pending'])
    with col4:
        st.metric("Completion Rate", f"{stats['completion_rate']}%")
    
    st.divider()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### By Category")
        if stats['by_category']:
            for cat, count in stats['by_category'].items():
                emoji = {'task': '✓', 'idea': '💡', 'worry': '⚠️'}[cat]
                st.metric(f"{emoji} {cat.capitalize()}", count)
        else:
            st.info("No data yet")
    
    with col2:
        st.markdown("### By Priority")
        if stats['by_priority']:
            for pri, count in stats['by_priority'].items():
                st.metric(pri.capitalize(), count)
        else:
            st.info("No data yet")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**About**")
    st.markdown("Axon Intelligence v1.0")

with col2:
    st.markdown("**Data**")
    st.markdown("Stored locally (JSON)")

with col3:
    st.markdown("**Status**")
    st.markdown("✓ Operational")

st.markdown("""
<div style="text-align: center; color: #6b7280; font-size: 0.9em; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e5e7eb;">
<p>🧠 <strong>Axon Intelligence</strong></p>
<p>Production-ready thought organization system</p>
</div>
""", unsafe_allow_html=True)