#!/usr/bin/env python3
"""
Axon Intelligence - Production-Ready Application
SaaS-style interface with professional design
"""

import streamlit as st
from models import Category, Priority
from storage import StorageManager
from logic import ThoughtManager
from datetime import datetime


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
    /* Color Variables */
    :root {
        --primary: #2563eb;
        --primary-dark: #1e40af;
        --primary-light: #3b82f6;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --bg-primary: #ffffff;
        --bg-secondary: #f9fafb;
        --bg-tertiary: #f3f4f6;
        --text-primary: #111827;
        --text-secondary: #6b7280;
        --border: #e5e7eb;
    }
    
    /* Global Styles */
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
    
    /* Header Styling */
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
    
    /* Card Styling */
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
    
    /* Metric Cards */
    .metric-card {
        background: var(--bg-primary);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 20px;
        text-align: center;
    }
    
    /* Badge Styling */
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
    
    /* Buttons */
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
    
    /* Input Fields */
    .stTextArea textarea, .stTextInput input, .stSelectbox select {
        background-color: var(--bg-primary);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 10px 12px;
        color: var(--text-primary);
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus, .stSelectbox select:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    /* Messages */
    .stSuccess {
        background-color: #f0fdf4;
        border: 1px solid #86efac;
        color: #166534;
    }
    
    .stError {
        background-color: #fef2f2;
        border: 1px solid #fca5a5;
        color: #7f1d1d;
    }
    
    .stInfo {
        background-color: #f0f9ff;
        border: 1px solid #93c5fd;
        color: #0c4a6e;
    }
    
    /* Table Styling */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 6px;
    }
    
    /* Divider */
    hr {
        border: none;
        border-top: 1px solid var(--border);
        margin: 20px 0;
    }
    
    /* Grid Layout */
    .grid-2 {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
    }
    
    .grid-3 {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 20px;
    }
    
    .grid-4 {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .header-title {
            font-size: 1.8rem;
        }
        .grid-2, .grid-3, .grid-4 {
            grid-template-columns: 1fr;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZATION
# ============================================================================

# Initialize managers
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
    
    # Stats
    stats = st.session_state.manager.get_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total", stats['total'])
    with col2:
        st.metric("Completed", stats['completed'])
    
    st.markdown("---")
    
    # Export
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
    # Header
    st.markdown("""
        <div class="header-container">
            <div class="header-title">🧠 Axon Intelligence</div>
            <div class="header-subtitle">Organize your thoughts. Understand your priorities.</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Main intro
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("""
        ### Welcome to Axon
        
        Axon helps you capture and organize your thoughts effortlessly.
        Whether it's a task to complete, an idea to explore, or a worry to process,
        Axon gives you clarity and prioritization.
        
        **Key Features:**
        - 📝 Capture thoughts instantly
        - 🏷️ Auto-categorize (Tasks, Ideas, Worries)
        - ⭐ Prioritize what matters
        - 📊 View analytics and insights
        - 💾 Everything saved locally
        """)
        
        st.markdown("")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("➕ Create Your First Thought", use_container_width=True, type="primary"):
                st.switch_page("pages/new_thought.py") if hasattr(st, 'switch_page') else None
        with col_b:
            if st.button("📋 View All Thoughts", use_container_width=True):
                st.switch_page("pages/all_thoughts.py") if hasattr(st, 'switch_page') else None
    
    with col2:
        st.markdown("### Quick Stats")
        
        stats = st.session_state.manager.get_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Thoughts", stats['total'])
        with col2:
            st.metric("Completed", stats['completed'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Pending", stats['pending'])
        with col2:
            st.metric("Completion", f"{stats['completion_rate']}%")
    
    st.divider()
    
    # Categories breakdown
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
    # Header
    st.markdown("""
        <div class="header-container">
            <div class="header-title">Add a New Thought</div>
            <div class="header-subtitle">Capture what's on your mind</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Input form
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
    
    # Buttons
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
    # Header
    st.markdown("""
        <div class="header-container">
            <div class="header-title">Your Thoughts</div>
            <div class="header-subtitle">Manage and organize your ideas</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Filters
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
    
    # Get thoughts
    thoughts = st.session_state.manager.get_all()
    
    # Apply search
    if search_query:
        thoughts = st.session_state.manager.search(search_query)
    
    # Apply filters
    if filter_category:
        thoughts = [t for t in thoughts if t.category == filter_category]
    
    if filter_priority:
        thoughts = [t for t in thoughts if t.priority == filter_priority]
    
    if filter_status == "Pending":
        thoughts = [t for t in thoughts if not t.completed]
    elif filter_status == "Completed":
        thoughts = [t for t in thoughts if t.completed]
    
    # Sort
    thoughts = st.session_state.manager.sort_by_priority(thoughts)
    thoughts = st.session_state.manager.sort_by_date(thoughts, newest_first=True)
    
    # Display
    if not thoughts:
        st.info("No thoughts found.")
    else:
        st.markdown(f"**{len(thoughts)} thought{'s' if len(thoughts) != 1 else ''} found**")
        st.divider()
        
        for thought in thoughts:
            col1, col2 = st.columns([0.1, 0.9])
            
            with col1:
                # Checkbox to complete
                is_checked = st.checkbox(
                    "",
                    value=thought.completed,
                    key=f"complete_{thought.id}"
                )
                
                if is_checked != thought.completed:
                    st.session_state.manager.toggle_complete(thought.id)
                    st.rerun()
            
            with col2:
                # Category emoji and badge
                category_emoji = {'task': '✓', 'idea': '💡', 'worry': '⚠️'}
                category_badge = f'<span class="badge badge-{thought.category.value}">{category_emoji[thought.category.value]} {thought.category.value.capitalize()}</span>'
                
                # Priority badge
                priority_badge = f'<span class="badge badge-{thought.priority.value}">{thought.priority.value.capitalize()}</span>'
                
                # Display
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
                
                # Delete button
                if st.button("🗑️ Delete", key=f"delete_{thought.id}"):
                    st.session_state.manager.delete_thought(thought.id)
                    st.success("Deleted")
                    st.rerun()

# ============================================================================
# PAGE: ANALYTICS
# ============================================================================

elif page == "📊 Analytics":
    # Header
    st.markdown("""
        <div class="header-container">
            <div class="header-title">Analytics</div>
            <div class="header-subtitle">Insights into your thoughts</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    stats = st.session_state.manager.get_stats()
    
    # Top metrics
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
    
    # Category breakdown
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