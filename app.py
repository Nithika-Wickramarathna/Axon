#!/usr/bin/env python3
"""
Axon Intelligence - Production Edition
Modern Crypto Dashboard UI with glassmorphism and advanced features
"""

import streamlit as st
from models import Category, Priority, Status
from storage import StorageManager
from logic import ThoughtManager
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# PAGE CONFIG & THEME
# ============================================================================

st.set_page_config(
    page_title="Axon Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern crypto dashboard theme with glassmorphism
st.markdown("""
    <style>
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --accent: #06b6d4;
        --success: #10b981;
        --danger: #ef4444;
        --warning: #f59e0b;
        --bg: #0f172a;
        --bg-secondary: #1e293b;
        --bg-tertiary: #334155;
        --border: #475569;
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
    }
    
    * { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: var(--text-primary);
    }
    
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(100, 116, 139, 0.2);
    }
    
    .header {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(6, 182, 212, 0.05));
        border: 1px solid rgba(99, 102, 241, 0.2);
        backdrop-filter: blur(10px);
        padding: 30px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    
    .stat-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(6, 182, 212, 0.05));
        border: 1px solid rgba(99, 102, 241, 0.2);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(6, 182, 212, 0.1));
    }
    
    .thought-card {
        background: linear-gradient(135deg, rgba(51, 65, 85, 0.4), rgba(30, 41, 59, 0.6));
        border: 1px solid rgba(99, 102, 241, 0.2);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .thought-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.1);
    }
    
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 4px;
    }
    
    .badge-task {
        background: rgba(16, 185, 129, 0.2);
        color: #6ee7b7;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    
    .badge-idea {
        background: rgba(99, 102, 241, 0.2);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.4);
    }
    
    .badge-worry {
        background: rgba(239, 68, 68, 0.2);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    
    .badge-high {
        background: rgba(239, 68, 68, 0.15);
        color: #fca5a5;
    }
    
    .badge-medium {
        background: rgba(245, 158, 11, 0.15);
        color: #fcd34d;
    }
    
    .badge-low {
        background: rgba(16, 185, 129, 0.15);
        color: #6ee7b7;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #4f46e5);
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #4f46e5, #4338ca);
        box-shadow: 0 8px 16px rgba(99, 102, 241, 0.3);
        transform: translateY(-2px);
    }
    
    .divider {
        border-top: 1px solid rgba(100, 116, 139, 0.2);
        margin: 20px 0;
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
    st.markdown("### 🧠 Axon Intelligence")
    st.markdown("*Advanced Thought Organization*")
    st.divider()
    
    page = st.radio(
        "Navigation",
        ["🏠 Home", "➕ Create", "📋 Browse", "📊 Analytics"],
        label_visibility="collapsed"
    )
    
    st.divider()
    st.markdown("### ⚡ Quick Stats")
    
    analytics = st.session_state.manager.get_analytics()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total", analytics.total_thoughts)
        st.metric("Active", analytics.active_thoughts)
    with col2:
        st.metric("Completed", analytics.completed_thoughts)
        st.metric("Archived", analytics.archived_thoughts)
    
    st.divider()
    st.metric("Completion Rate", f"{analytics.completion_rate}%")
    st.metric("AI Confidence", f"{analytics.avg_confidence:.0%}")
    
    st.divider()
    
    # Export
    csv_data = st.session_state.manager.export_csv()
    if csv_data:
        st.download_button(
            "📥 Export CSV",
            csv_data,
            f"axon_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv",
            use_container_width=True
        )

# ============================================================================
# PAGE: HOME
# ============================================================================

if page == "🏠 Home":
    st.markdown('<div class="header"><h1>🧠 Axon Intelligence</h1><p>Advanced Thought Organization & AI-Powered Insights</p></div>', unsafe_allow_html=True)
    
    analytics = st.session_state.manager.get_analytics()
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("📝 Total", analytics.total_thoughts)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("✓ Completed", analytics.completed_thoughts)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("🔄 Active", analytics.active_thoughts)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("🤖 AI Confidence", f"{analytics.avg_confidence:.0%}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        if analytics.by_category:
            df_cat = {"Category": list(analytics.by_category.keys()), "Count": list(analytics.by_category.values())}
            fig = px.bar(df_cat, x="Category", y="Count", color="Category",
                        color_discrete_map={"task": "#10b981", "idea": "#6366f1", "worry": "#ef4444"},
                        title="Thoughts by Category")
            fig.update_layout(template="plotly_dark", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if analytics.by_priority:
            df_pri = {"Priority": list(analytics.by_priority.keys()), "Count": list(analytics.by_priority.values())}
            fig = px.pie(df_pri, values="Count", names="Priority", title="Priority Distribution",
                        color_discrete_map={"high": "#ef4444", "medium": "#f59e0b", "low": "#10b981"})
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE: CREATE
# ============================================================================

elif page == "➕ Create":
    st.markdown('<div class="header"><h1>Create New Thought</h1></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        text = st.text_area(
            "What's on your mind?",
            placeholder="Type your thought...",
            height=150,
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("**🤖 AI Suggestions**")
        if text:
            auto_category = st.session_state.manager._auto_detect_category(text)
            auto_priority = st.session_state.manager._auto_detect_priority(text)
            
            st.write(f"📂 {auto_category.value.upper()}")
            st.write(f"⭐ {auto_priority.value.upper()}")
            
            category = st.selectbox("Category", list(Category), index=list(Category).index(auto_category))
            priority = st.selectbox("Priority", list(Priority), index=list(Priority).index(auto_priority))
        else:
            category = Category.IDEA
            priority = Priority.MEDIUM
    
    st.divider()
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("✨ Create", use_container_width=True, type="primary"):
            success, message, thought = st.session_state.manager.create_thought(text, category, priority)
            
            if success:
                st.success(message)
                st.balloons()
                st.rerun()
            else:
                st.error(message)

# ============================================================================
# PAGE: BROWSE
# ============================================================================

elif page == "📋 Browse":
    st.markdown('<div class="header"><h1>Your Thoughts</h1></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        search = st.text_input("🔍 Search")
    
    with col2:
        category_filter = st.selectbox("Category", [None] + list(Category), format_func=lambda x: "All" if x is None else x.value)
    
    with col3:
        priority_filter = st.selectbox("Priority", [None] + list(Priority), format_func=lambda x: "All" if x is None else x.value)
    
    with col4:
        status_filter = st.selectbox("Status", ["All", "Active", "Completed"])
    
    # Get thoughts
    thoughts = st.session_state.manager.get_thoughts(
        search=search if search else None,
        category=category_filter,
        priority=priority_filter,
        sort_by="priority_date"
    )
    
    if not thoughts:
        st.info("No thoughts found")
    else:
        st.markdown(f"**{len(thoughts)} thoughts**")
        st.divider()
        
        for thought in thoughts:
            col1, col2 = st.columns([0.1, 0.9])
            
            with col1:
                completed = st.checkbox(
                    "",
                    value=(thought.status == Status.COMPLETED),
                    key=f"cb_{thought.id}"
                )
                
                if completed != (thought.status == Status.COMPLETED):
                    st.session_state.manager.toggle_complete(thought.id)
                    st.rerun()
            
            with col2:
                st.markdown('<div class="thought-card">', unsafe_allow_html=True)
                
                col_a, col_b = st.columns([0.9, 0.1])
                
                with col_a:
                    st.markdown(f"<span class='badge badge-{thought.category.value}'>📂 {thought.category.value}</span>", unsafe_allow_html=True)
                    st.markdown(f"<span class='badge badge-{thought.priority.value}'>⭐ {thought.priority.value}</span>", unsafe_allow_html=True)
                    st.caption(f"{thought.confidence:.0%} confidence")
                
                with col_b:
                    if st.button("🗑️", key=f"del_{thought.id}"):
                        st.session_state.manager.delete_thought(thought.id)
                        st.rerun()
                
                style = "opacity: 0.6; text-decoration: line-through;" if thought.status == Status.COMPLETED else ""
                st.markdown(f"<div style='{style}'>{thought.text}</div>", unsafe_allow_html=True)
                st.caption(f"📅 {thought.created_at[:10]}")
                
                st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# PAGE: ANALYTICS
# ============================================================================

elif page == "📊 Analytics":
    st.markdown('<div class="header"><h1>Analytics Dashboard</h1></div>', unsafe_allow_html=True)
    
    analytics = st.session_state.manager.get_analytics()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📝 Total", analytics.total_thoughts)
    with col2:
        st.metric("✓ Completed", analytics.completed_thoughts)
    with col3:
        st.metric("🔄 Active", analytics.active_thoughts)
    with col4:
        st.metric("📦 Archived", analytics.archived_thoughts)
    with col5:
        st.metric("📈 Rate", f"{analytics.completion_rate}%")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if analytics.by_category:
            df_cat = {"Category": list(analytics.by_category.keys()), "Count": list(analytics.by_category.values())}
            fig = px.bar(df_cat, x="Category", y="Count", color="Category",
                        color_discrete_map={"task": "#10b981", "idea": "#6366f1", "worry": "#ef4444"},
                        title="By Category")
            fig.update_layout(template="plotly_dark", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if analytics.by_priority:
            df_pri = {"Priority": list(analytics.by_priority.keys()), "Count": list(analytics.by_priority.values())}
            fig = px.bar(df_pri, x="Priority", y="Count", color="Priority",
                        color_discrete_map={"high": "#ef4444", "medium": "#f59e0b", "low": "#10b981"},
                        title="By Priority")
            fig.update_layout(template="plotly_dark", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption("<div style='text-align: center;'>🧠 Axon Intelligence | Advanced Thought Organization</div>", unsafe_allow_html=True)