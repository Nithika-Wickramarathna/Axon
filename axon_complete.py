#!/usr/bin/env python3
"""
Axon Unwind - Interactive Thought Unwinding Assistant
Guided workflow with premium ecommerce colors
"""

import streamlit as st
import json
import os
from datetime import datetime
from enum import Enum
from uuid import uuid4
from dataclasses import dataclass, field
from typing import Optional, List

# ============================================================================
# DATA MODELS
# ============================================================================

class Category(str, Enum):
    TASK = "task"
    IDEA = "idea"
    WORRY = "worry"

@dataclass
class Thought:
    text: str
    category: Category = Category.TASK
    impact_score: int = 3
    urgency_score: int = 3
    priority_score: int = field(default=9, init=False)
    action_plan: Optional[str] = None
    is_controllable: Optional[bool] = None
    status: str = "active"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_deleted: bool = False
    
    def __post_init__(self):
        self.priority_score = self.impact_score * self.urgency_score
    
    def to_dict(self) -> dict:
        return {
            'text': self.text,
            'category': self.category.value,
            'impact_score': self.impact_score,
            'urgency_score': self.urgency_score,
            'priority_score': self.priority_score,
            'action_plan': self.action_plan,
            'is_controllable': self.is_controllable,
            'status': self.status,
            'id': self.id,
            'created_at': self.created_at,
            'is_deleted': self.is_deleted
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Thought':
        return cls(
            text=data['text'],
            category=Category(data['category']),
            impact_score=data.get('impact_score', 3),
            urgency_score=data.get('urgency_score', 3),
            action_plan=data.get('action_plan'),
            is_controllable=data.get('is_controllable'),
            status=data.get('status', 'active'),
            id=data.get('id'),
            created_at=data.get('created_at'),
            is_deleted=data.get('is_deleted', False)
        )

# ============================================================================
# STORAGE
# ============================================================================

class StorageManager:
    def __init__(self, filename: str = "axon_unwind_thoughts.json"):
        self.filename = filename
    
    def load(self) -> List[Thought]:
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    return [Thought.from_dict(item) for item in data if not item.get('is_deleted', False)]
        except:
            pass
        return []
    
    def save(self, thoughts: List[Thought]) -> bool:
        try:
            with open(self.filename, 'w') as f:
                data = [thought.to_dict() for thought in thoughts]
                json.dump(data, f, indent=2)
            return True
        except:
            return False
    
    def add(self, thought: Thought) -> bool:
        thoughts = self.load()
        thoughts.append(thought)
        return self.save(thoughts)
    
    def update(self, thought_id: str, thought: Thought) -> bool:
        all_thoughts = self._load_all()
        for i, t in enumerate(all_thoughts):
            if t.id == thought_id:
                all_thoughts[i] = thought
                return self._save_all(all_thoughts)
        return False
    
    def _load_all(self) -> List[Thought]:
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    return [Thought.from_dict(item) for item in json.load(f)]
        except:
            pass
        return []
    
    def _save_all(self, thoughts: List[Thought]) -> bool:
        try:
            with open(self.filename, 'w') as f:
                json.dump([t.to_dict() for t in thoughts], f, indent=2)
            return True
        except:
            return False

# ============================================================================
# STREAMLIT CONFIG
# ============================================================================

st.set_page_config(page_title="Axon Unwind", page_icon="🧠", layout="wide")

# Premium ecommerce colors
COLORS = {
    'primary': '#2c3e50',      # Dark blue-gray
    'secondary': '#34495e',    # Lighter blue-gray
    'accent': '#e74c3c',       # Coral red
    'success': '#27ae60',       # Green
    'warning': '#f39c12',       # Orange
    'danger': '#e74c3c',        # Red
    'light_bg': '#ecf0f1',     # Light gray
    'text': '#2c3e50',          # Dark text
}

st.markdown(f"""
    <style>
    * {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
    }}
    
    body, [data-testid="stAppViewContainer"] {{
        background-color: {COLORS['light_bg']};
        color: {COLORS['text']};
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {COLORS['primary']};
    }}
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
        color: white;
    }}
    
    .stButton > button {{
        background-color: {COLORS['accent']} !important;
        color: white !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }}
    
    .stButton > button:hover {{
        background-color: #d63b2f !important;
    }}
    
    .step-box {{
        background: white;
        border-left: 4px solid {COLORS['accent']};
        padding: 16px;
        border-radius: 8px;
        margin: 16px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    .card {{
        background: white;
        padding: 16px;
        border-radius: 8px;
        margin: 8px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    
    .priority-critical {{
        color: {COLORS['danger']};
        font-weight: bold;
        font-size: 20px;
    }}
    
    .priority-important {{
        color: {COLORS['warning']};
        font-weight: bold;
        font-size: 20px;
    }}
    
    .priority-low {{
        color: {COLORS['success']};
        font-weight: bold;
        font-size: 20px;
    }}
    
    .metric {{
        background: white;
        padding: 16px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    
    input, textarea, select {{
        border-radius: 6px !important;
        border: 1px solid #d0d0d0 !important;
    }}
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZE
# ============================================================================

if 'storage' not in st.session_state:
    st.session_state.storage = StorageManager()
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

# ============================================================================
# MAIN INTERFACE
# ============================================================================

st.markdown(f"<h1 style='color: {COLORS['primary']};'>🧠 Axon Unwind</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 18px; color: #666;'><i>Transform your messy thoughts into clear action</i></p>", unsafe_allow_html=True)
st.divider()

# Step navigation
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("1️⃣ Brain Dump", use_container_width=True):
        st.session_state.current_step = 1
        st.rerun()

with col2:
    if st.button("2️⃣ Score", use_container_width=True):
        st.session_state.current_step = 2
        st.rerun()

with col3:
    if st.button("3️⃣ View", use_container_width=True):
        st.session_state.current_step = 3
        st.rerun()

with col4:
    if st.button("4️⃣ Plan", use_container_width=True):
        st.session_state.current_step = 4
        st.rerun()

with col5:
    if st.button("5️⃣ Clarity", use_container_width=True):
        st.session_state.current_step = 5
        st.rerun()

st.divider()

# ============================================================================
# STEP 1: BRAIN DUMP
# ============================================================================

if st.session_state.current_step == 1:
    st.markdown(f"<h2 style='color: {COLORS['primary']};'>Step 1️⃣: Brain Dump Everything</h2>", unsafe_allow_html=True)
    st.write("**No filtering. No judgment. Just write it down.**")
    
    st.markdown(f"""
    <div class="step-box">
    💡 <b>Write freely:</b> Don't worry about grammar, organization, or importance. Just get everything out of your head.
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    thought_text = st.text_area(
        "What's on your mind?",
        placeholder="Example:\n- Worried about deadline\n- Haven't called mom\n- Need to fix bug\n- Should learn AI\n- Feeling overwhelmed",
        height=200,
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col3:
        if st.button("Save & Continue", use_container_width=True, type="primary"):
            if thought_text.strip():
                thought = Thought(text=thought_text.strip(), category=Category.TASK)
                st.session_state.storage.add(thought)
                st.success("✓ Saved!")
                st.session_state.current_step = 2
                st.rerun()
            else:
                st.error("Please write something")

# ============================================================================
# STEP 2: SCORING
# ============================================================================

elif st.session_state.current_step == 2:
    st.markdown(f"<h2 style='color: {COLORS['primary']};'>Step 2️⃣: Score Your Thoughts</h2>", unsafe_allow_html=True)
    st.write("**Rate Impact & Urgency to find your priorities**")
    
    thoughts = st.session_state.storage.load()
    
    if not thoughts:
        st.warning("No thoughts yet. Go to Step 1.")
    else:
        st.markdown(f"""
        <div class="step-box">
        <b>🔥 Impact (1-5):</b> How important to your future?<br>
        <b>⏳ Urgency (1-5):</b> Does it need action now?<br>
        <b>Priority Score = Impact × Urgency</b>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        unscored = [t for t in thoughts if t.impact_score == 3 and t.urgency_score == 3 and len(thoughts) > 1]
        
        if unscored:
            thought = unscored[0]
            st.markdown(f"<h3 style='color: {COLORS['accent']};'>📌 {thought.text}</h3>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                impact = st.slider("🔥 Impact Score", 1, 5, 3)
            
            with col2:
                urgency = st.slider("⏳ Urgency Score", 1, 5, 3)
            
            priority_score = impact * urgency
            
            if priority_score >= 20:
                st.markdown(f"<div style='font-size: 28px; color: {COLORS['danger']}; font-weight: bold;'>🔴 {priority_score} pts - CRITICAL</div>", unsafe_allow_html=True)
            elif priority_score >= 12:
                st.markdown(f"<div style='font-size: 28px; color: {COLORS['warning']}; font-weight: bold;'>🟠 {priority_score} pts - IMPORTANT</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='font-size: 28px; color: {COLORS['success']}; font-weight: bold;'>🟢 {priority_score} pts - LOW</div>", unsafe_allow_html=True)
            
            st.divider()
            
            if st.button("✓ Save & Next", use_container_width=True, type="primary"):
                thought.impact_score = impact
                thought.urgency_score = urgency
                thought.priority_score = priority_score
                st.session_state.storage.update(thought.id, thought)
                st.rerun()
        
        else:
            st.success("✓ All thoughts scored!")
            
            st.subheader("Ranked by Priority")
            sorted_thoughts = sorted(thoughts, key=lambda t: t.priority_score, reverse=True)
            
            for thought in sorted_thoughts:
                if thought.priority_score >= 20:
                    st.markdown(f"🔴 **{thought.priority_score} pts** | {thought.text}")
                elif thought.priority_score >= 12:
                    st.markdown(f"🟠 **{thought.priority_score} pts** | {thought.text}")
                else:
                    st.markdown(f"🟢 **{thought.priority_score} pts** | {thought.text}")
            
            st.divider()
            
            if st.button("Continue to Step 3", use_container_width=True, type="primary"):
                st.session_state.current_step = 3
                st.rerun()

# ============================================================================
# STEP 3: VIEW ALL
# ============================================================================

elif st.session_state.current_step == 3:
    st.markdown(f"<h2 style='color: {COLORS['primary']};'>Step 3️⃣: View All Thoughts</h2>", unsafe_allow_html=True)
    
    thoughts = st.session_state.storage.load()
    
    if not thoughts:
        st.info("No thoughts yet.")
    else:
        sorted_thoughts = sorted(thoughts, key=lambda t: t.priority_score, reverse=True)
        
        st.markdown(f"""
        <div class="step-box">
        ✓ Your brain is now organized<br>
        ✓ You can see what matters most<br>
        ✓ Everything is ranked
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        for thought in sorted_thoughts:
            with st.expander(f"[{thought.priority_score} pts] {thought.text}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if thought.priority_score >= 20:
                        st.markdown(f"<span style='color: {COLORS['danger']}; font-weight: bold;'>🔴 CRITICAL</span>", unsafe_allow_html=True)
                    elif thought.priority_score >= 12:
                        st.markdown(f"<span style='color: {COLORS['warning']}; font-weight: bold;'>🟠 IMPORTANT</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='color: {COLORS['success']}; font-weight: bold;'>🟢 LOW</span>", unsafe_allow_html=True)
                
                with col2:
                    st.write(f"🔥 Impact: {thought.impact_score}/5")
                
                with col3:
                    st.write(f"⏳ Urgency: {thought.urgency_score}/5")
        
        st.divider()
        
        if st.button("Continue to Step 4", use_container_width=True, type="primary"):
            st.session_state.current_step = 4
            st.rerun()

# ============================================================================
# STEP 4: ACTION PLANNING
# ============================================================================

elif st.session_state.current_step == 4:
    st.markdown(f"<h2 style='color: {COLORS['primary']};'>Step 4️⃣: Create Action Plans</h2>", unsafe_allow_html=True)
    
    thoughts = st.session_state.storage.load()
    
    if not thoughts:
        st.info("No thoughts yet.")
    else:
        critical = [t for t in thoughts if t.priority_score >= 12]
        
        if not critical:
            st.info("No critical items.")
        else:
            st.markdown(f"""
            <div class="step-box">
            For each critical thought:<br>
            1. Why does it matter?<br>
            2. What's the smallest next step?<br>
            3. When will you do it?
            </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            
            for thought in critical[:3]:
                with st.expander(f"[{thought.priority_score} pts] {thought.text}"):
                    st.write("**Why does this matter?**")
                    why = st.text_area("", value=thought.action_plan or "", height=80, label_visibility="collapsed", key=f"why_{thought.id}")
                    
                    st.write("**Next action?**")
                    next_step = st.text_input("", placeholder="e.g., Review requirements (30 min)", key=f"step_{thought.id}")
                    
                    st.write("**When?**")
                    when = st.selectbox("", ["Today", "Tomorrow", "This week", "Next week"], key=f"when_{thought.id}")
                    
                    if st.button("✓ Save", key=f"save_{thought.id}"):
                        thought.action_plan = f"{why}\n\nNext step: {next_step}\nWhen: {when}"
                        st.session_state.storage.update(thought.id, thought)
                        st.success("Saved!")
        
        st.divider()
        
        if st.button("Continue to Step 5", use_container_width=True, type="primary"):
            st.session_state.current_step = 5
            st.rerun()

# ============================================================================
# STEP 5: FINAL CLARITY
# ============================================================================

elif st.session_state.current_step == 5:
    st.markdown(f"<h2 style='color: {COLORS['primary']};'>Step 5️⃣: Achieve Clarity</h2>", unsafe_allow_html=True)
    
    thoughts = st.session_state.storage.load()
    
    if not thoughts:
        st.info("No thoughts yet.")
    else:
        st.markdown(f"""
        <div class="step-box">
        ✓ Brain dump → Complete<br>
        ✓ Scored & ranked → Complete<br>
        ✓ Action plans → Complete<br>
        <b>Now: See your clear path forward</b>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        
        critical = [t for t in thoughts if t.priority_score >= 20]
        important = [t for t in thoughts if 12 <= t.priority_score < 20]
        low = [t for t in thoughts if t.priority_score < 12]
        
        with col1:
            st.markdown(f"<div class='metric'><span style='color: {COLORS['danger']}; font-size: 24px;'>🔴</span><br><b>{len(critical)}</b><br>Critical</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"<div class='metric'><span style='color: {COLORS['warning']}; font-size: 24px;'>🟠</span><br><b>{len(important)}</b><br>Important</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"<div class='metric'><span style='color: {COLORS['success']}; font-size: 24px;'>🟢</span><br><b>{len(low)}</b><br>Low</div>", unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown(f"<h3 style='color: {COLORS['accent']};'>🎯 Your Focus Today/Tomorrow</h3>", unsafe_allow_html=True)
        
        if critical:
            for thought in critical[:2]:
                st.markdown(f"<div class='card'><b style='color: {COLORS['danger']};'>[{thought.priority_score} pts]</b> {thought.text}</div>", unsafe_allow_html=True)
        else:
            st.info("No critical items")
        
        st.divider()
        
        st.markdown(f"<h3 style='color: {COLORS['primary']};'>✓ Everything Else</h3>", unsafe_allow_html=True)
        
        for thought in important:
            st.markdown(f"<div class='card'>• [{thought.priority_score} pts] {thought.text}</div>", unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown(f"<h3 style='color: {COLORS['primary']};'>💭 Your Reflection</h3>", unsafe_allow_html=True)
        
        reflection = st.text_area("How do you feel now?", height=100, label_visibility="collapsed", placeholder="Write your feelings...")
        
        if st.button("✓ Complete Session", use_container_width=True, type="primary"):
            st.success("""
            ✓ You've unwound your messy thoughts!
            
            You now have:
            ✅ Clear priorities
            ✅ Ranked by importance
            ✅ Action plans for top items
            ✅ Peace of mind
            """)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown(f"<h2 style='color: white;'>🧠 Axon Unwind</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: rgba(255,255,255,0.7);'>From chaos to clarity</p>", unsafe_allow_html=True)
    
    st.divider()
    
    thoughts = st.session_state.storage.load()
    st.metric("Thoughts", len(thoughts))
    
    if thoughts:
        critical = len([t for t in thoughts if t.priority_score >= 20])
        st.metric("Critical", critical)
    
    st.divider()
    
    if st.button("Clear & Start Fresh", use_container_width=True):
        if os.path.exists(st.session_state.storage.filename):
            os.remove(st.session_state.storage.filename)
        st.rerun()

st.divider()
st.caption("Axon Unwind • From chaos to clarity in 5 steps")