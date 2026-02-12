#!/usr/bin/env python3
"""
Axon Intelligence - Premium Dark Theme Edition
Beautiful UI inspired by modern tech website design
"""

import streamlit as st
import json
import os
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from difflib import SequenceMatcher
import re


# ============================================================================
# CORE INTELLIGENCE ENGINE
# ============================================================================

class ThoughtIntelligence:
    """Core reasoning engine for thought analysis"""
    
    def __init__(self):
        self.task_signals = {
            'need to', 'must', 'have to', 'should', 'will', 'finish', 'complete',
            'do', 'make', 'call', 'email', 'buy', 'deadline', 'asap', 'urgent'
        }
        
        self.worry_signals = {
            'stressed', 'worried', 'anxious', 'afraid', 'scared', 'fail',
            'overwhelmed', 'terrified', 'panic', 'lose', 'mistake', 'concerned'
        }
        
        self.idea_signals = {
            'maybe', 'could', 'might', 'what if', 'imagine', 'try', 'build',
            'create', 'design', 'explore', 'experiment', 'startup', 'learn'
        }
    
    def classify_thought(self, text: str) -> dict:
        """Classify thought with confidence scoring"""
        if not text:
            return {'type': 'idea', 'confidence': 0.5, 'reasoning': 'Empty text'}
        
        text_lower = text.lower()
        
        task_score = sum(1 for signal in self.task_signals if signal in text_lower)
        worry_score = sum(1 for signal in self.worry_signals if signal in text_lower)
        idea_score = sum(1 for signal in self.idea_signals if signal in text_lower)
        
        caps_count = sum(1 for c in text if c.isupper())
        caps_ratio = caps_count / max(len(text), 1)
        
        if caps_ratio > 0.20:
            worry_score += 1.5
        
        if text.count('!') > 1:
            idea_score += 0.5
        
        if text.count('?') > 1:
            worry_score += 0.5
        
        total = task_score + worry_score + idea_score
        
        if total == 0:
            return {
                'type': 'idea',
                'confidence': 0.5,
                'reasoning': 'No strong signals',
                'alternatives': [
                    {'type': 'task', 'confidence': 0.25},
                    {'type': 'worry', 'confidence': 0.25}
                ]
            }
        
        scores = {
            'task': task_score / total,
            'worry': worry_score / total,
            'idea': idea_score / total
        }
        
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary_type = sorted_scores[0][0]
        primary_confidence = min(sorted_scores[0][1], 0.99)
        
        alternatives = [
            {'type': t, 'confidence': min(c, 0.99)}
            for t, c in sorted_scores[1:] if c > 0.15
        ]
        
        return {
            'type': primary_type,
            'confidence': primary_confidence,
            'reasoning': self._generate_reasoning(text, primary_type),
            'alternatives': alternatives
        }
    
    def _generate_reasoning(self, text: str, thought_type: str) -> str:
        """Generate classification reasoning"""
        text_lower = text.lower()
        
        if thought_type == 'task':
            found = []
            if any(s in text_lower for s in ['need', 'must', 'should']):
                found.append('action words')
            if any(s in text_lower for s in ['deadline', 'asap', 'due']):
                found.append('urgency markers')
            if found:
                return f"Detected {', '.join(found)}"
            return "Has actionable components"
        
        elif thought_type == 'worry':
            found = []
            if any(s in text_lower for s in ['stressed', 'worried', 'anxious']):
                found.append('emotional words')
            if sum(1 for c in text if c.isupper()) / max(len(text), 1) > 0.2:
                found.append('emphasis')
            if found:
                return f"Detected {', '.join(found)}"
            return "Shows concern"
        
        else:
            return "Exploratory thought"
    
    def calculate_intensity(self, text: str) -> int:
        """Calculate intensity 1-10"""
        score = 1
        text_lower = text.lower()
        
        if any(w in text_lower for w in ['asap', 'today', 'must', 'critical']):
            score += 3
        
        if any(w in text_lower for w in ['stressed', 'terrified', 'hate', 'love']):
            score += 2
        
        if sum(1 for c in text if c.isupper()) / max(len(text), 1) > 0.20:
            score += 2
        
        if text.count('!') > 1:
            score += 1
        
        return min(score, 10)
    
    def find_similar_thoughts(self, thoughts: list, threshold: float = 0.65) -> list:
        """Find duplicate thoughts"""
        duplicates = []
        
        for i, t1 in enumerate(thoughts):
            for t2 in thoughts[i+1:]:
                similarity = SequenceMatcher(None, t1['text'].lower(), t2['text'].lower()).ratio()
                
                if similarity > threshold:
                    duplicates.append({
                        'id1': t1['id'],
                        'id2': t2['id'],
                        'text1': t1['text'][:60],
                        'text2': t2['text'][:60],
                        'similarity': round(similarity, 3)
                    })
        
        return sorted(duplicates, key=lambda x: x['similarity'], reverse=True)
    
    def analyze_intensity_trend(self, history: list) -> dict:
        """Analyze intensity trend"""
        if len(history) < 2:
            return {'trend': 'insufficient_data', 'insight': 'Need more data'}
        
        start = history[0]
        end = history[-1]
        difference = end - start
        
        if difference < -2:
            trend = '📈 IMPROVING'
        elif difference > 2:
            trend = '📉 WORSENING'
        else:
            trend = '➡️ STABLE'
        
        return {'trend': trend, 'start': start, 'end': end, 'change': difference}
    
    def get_next_action(self, thoughts: list) -> dict:
        """Get next action recommendation"""
        actionable = []
        for t in thoughts:
            if t['type'] == 'task' and t['status'] in ['pending', 'in-progress']:
                actionable.append(t)
            elif t['type'] == 'worry' and t['status'] in ['active', 'managed']:
                actionable.append(t)
        
        if not actionable:
            return {'has_recommendation': False, 'message': '✓ No urgent items!'}
        
        def score_thought(t):
            score = 0.5
            if t['type'] == 'task':
                score += 0.2
            if t['status'] == 'in-progress':
                score += 0.15
            intensity = t.get('intensity', 5)
            score += (intensity / 10) * 0.2
            created = datetime.fromisoformat(t['created'])
            age_days = (datetime.now() - created).days
            if age_days > 7:
                score += 0.15
            elif age_days > 3:
                score += 0.1
            return min(score, 1.0)
        
        best_action = max(actionable, key=score_thought)
        top_score = score_thought(best_action)
        
        return {
            'has_recommendation': True,
            'top_action': best_action,
            'score': round(top_score, 2)
        }
    
    def analyze_patterns(self, thoughts: list) -> dict:
        """Find patterns"""
        if not thoughts:
            return {'total': 0}
        
        type_counts = Counter(t['type'] for t in thoughts)
        status_counts = Counter(t['status'] for t in thoughts)
        
        intensity_by_type = {}
        for t_type in ['task', 'worry', 'idea']:
            type_thoughts = [t for t in thoughts if t['type'] == t_type]
            if type_thoughts:
                avg = sum(t['intensity'] for t in type_thoughts) / len(type_thoughts)
                intensity_by_type[t_type] = round(avg, 1)
        
        keywords = []
        stop_words = {'i', 'the', 'a', 'an', 'is', 'are', 'to', 'of', 'and', 'or', 'but'}
        
        for t in thoughts:
            words = t['text'].lower().split()
            for word in words:
                clean_word = word.strip('.,!?;:')
                if len(clean_word) > 3 and clean_word not in stop_words:
                    keywords.append(clean_word)
        
        top_keywords = Counter(keywords).most_common(5)
        
        return {
            'total': len(thoughts),
            'type_breakdown': dict(type_counts),
            'avg_intensity_by_type': intensity_by_type,
            'top_keywords': top_keywords
        }


# ============================================================================
# DATA MANAGEMENT
# ============================================================================

def load_thoughts_data():
    """Load thoughts"""
    if os.path.exists('axon_thoughts.json'):
        try:
            with open('axon_thoughts.json', 'r') as f:
                return json.load(f)
        except:
            return []
    return []


def save_thoughts_data(thoughts):
    """Save thoughts"""
    with open('axon_thoughts.json', 'w') as f:
        json.dump(thoughts, f, indent=2)


def create_thought_object(text: str, classification: dict, intensity: int) -> dict:
    """Create thought object"""
    default_status = {
        'task': 'pending',
        'worry': 'active',
        'idea': 'raw'
    }
    
    return {
        'id': int(datetime.now().timestamp() * 1000),
        'text': text,
        'type': classification['type'],
        'confidence': classification['confidence'],
        'intensity': intensity,
        'intensity_history': [intensity],
        'created': datetime.now().isoformat(),
        'updated': datetime.now().isoformat(),
        'status': default_status.get(classification['type'], 'pending'),
        'user_corrected': False
    }


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Axon Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Dark Theme Styling
st.markdown("""
    <style>
    /* Root Colors - Premium Dark Theme */
    :root {
        --bg-primary: #0a0e27;
        --bg-secondary: #12172a;
        --bg-tertiary: #1a2043;
        --accent-blue: #3b82f6;
        --accent-purple: #8b5cf6;
        --accent-cyan: #06b6d4;
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
        --border-color: #1e293b;
        --gradient-1: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        --gradient-2: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
    }
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }
    
    [data-testid="stSidebar"] {
        background-color: var(--bg-secondary);
        border-right: 1px solid var(--border-color);
    }
    
    /* Main Content */
    .main {
        background-color: var(--bg-primary);
    }
    
    /* Text Styles */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Hero Title */
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: var(--gradient-1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        letter-spacing: -1px;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: var(--text-secondary);
        margin-bottom: 2rem;
        font-weight: 400;
        line-height: 1.6;
    }
    
    /* Cards */
    .card {
        background-color: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 24px;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .card:hover {
        border-color: var(--accent-blue);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.1);
        transform: translateY(-2px);
    }
    
    /* Stat Cards */
    .stat-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    /* Thought Cards */
    .thought-card {
        background-color: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        transition: all 0.3s ease;
    }
    
    .thought-card:hover {
        border-color: var(--accent-blue);
        background-color: rgba(59, 130, 246, 0.05);
    }
    
    .thought-card.task {
        border-left: 4px solid #ef4444;
    }
    
    .thought-card.worry {
        border-left: 4px solid #f59e0b;
    }
    
    .thought-card.idea {
        border-left: 4px solid #10b981;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .badge-task {
        background-color: rgba(239, 68, 68, 0.15);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .badge-worry {
        background-color: rgba(245, 158, 11, 0.15);
        color: #fcd34d;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .badge-idea {
        background-color: rgba(16, 185, 129, 0.15);
        color: #6ee7b7;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    /* Buttons */
    .stButton > button {
        background: var(--gradient-1);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(59, 130, 246, 0.4);
    }
    
    /* Input Fields */
    .stTextArea textarea {
        background-color: var(--bg-tertiary);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 12px;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--accent-blue);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    .stSelectbox, .stMultiselect {
        background-color: var(--bg-tertiary);
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, var(--border-color), transparent);
        margin: 2rem 0;
    }
    
    /* Grid Layout */
    .grid-2 {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 24px;
        margin: 24px 0;
    }
    
    .grid-3 {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 24px;
        margin: 24px 0;
    }
    
    .grid-4 {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 24px;
        margin: 24px 0;
    }
    
    /* Metric Styling */
    [data-testid="metric-container"] {
        background-color: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    /* Success/Info Messages */
    .stSuccess {
        background-color: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #6ee7b7;
        border-radius: 8px;
        padding: 16px;
    }
    
    .stInfo {
        background-color: rgba(59, 130, 246, 0.15);
        border: 1px solid rgba(59, 130, 246, 0.3);
        color: #93c5fd;
        border-radius: 8px;
        padding: 16px;
    }
    
    /* Intensity Colors */
    .intensity-1 { color: #10b981; }
    .intensity-2 { color: #10b981; }
    .intensity-3 { color: #10b981; }
    .intensity-4 { color: #f59e0b; }
    .intensity-5 { color: #f59e0b; }
    .intensity-6 { color: #f59e0b; }
    .intensity-7 { color: #ef4444; }
    .intensity-8 { color: #ef4444; }
    .intensity-9 { color: #ef4444; }
    .intensity-10 { color: #ef4444; }
    
    /* Confidence Colors */
    .confidence-high { color: #10b981; font-weight: 600; }
    .confidence-medium { color: #f59e0b; font-weight: 600; }
    .confidence-low { color: #ef4444; font-weight: 600; }
    
    /* Responsive */
    @media (max-width: 768px) {
        .grid-2, .grid-3, .grid-4 {
            grid-template-columns: 1fr;
        }
        
        .hero-title {
            font-size: 2.5rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'thoughts' not in st.session_state:
    st.session_state.thoughts = load_thoughts_data()

if 'intelligence' not in st.session_state:
    st.session_state.intelligence = ThoughtIntelligence()


# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

with st.sidebar:
    st.markdown("---")
    st.markdown("### 🧠 Axon Intelligence")
    st.markdown("Advanced thought organization")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["💭 Add Thought", "📚 All Thoughts", "📊 Analysis", "🎯 Recommendation"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### Statistics")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total", len(st.session_state.thoughts))
    with col2:
        tasks = sum(1 for t in st.session_state.thoughts if t['type'] == 'task')
        st.metric("Tasks", tasks)
    
    worries = sum(1 for t in st.session_state.thoughts if t['type'] == 'worry')
    ideas = sum(1 for t in st.session_state.thoughts if t['type'] == 'idea')
    
    st.markdown(f"**Worries:** {worries} | **Ideas:** {ideas}")
    st.markdown("---")
    st.markdown("_Local · Private · Intelligent_")


# ============================================================================
# PAGE: ADD THOUGHT
# ============================================================================

if page == "💭 Add Thought":
    # Hero Section
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown('<p class="hero-title">Add Your Thought</p>', unsafe_allow_html=True)
        st.markdown('<p class="hero-subtitle">Be honest. No structure needed. Axon will understand it.</p>', unsafe_allow_html=True)
    
    with col2:
        st.empty()
    
    st.divider()
    
    # Input Section
    st.markdown("### What's on your mind?")
    
    text = st.text_area(
        "Thought input",
        placeholder="Example: 'Need to finish the project by Friday but feeling stressed about it'",
        height=140,
        label_visibility="collapsed"
    )
    
    # Analyze Button
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col2:
        analyze_button = st.button("🤔 Analyze Thought", use_container_width=True, type="primary")
    
    if analyze_button and text.strip():
        st.divider()
        
        # Analyze
        intelligence = st.session_state.intelligence
        classification = intelligence.classify_thought(text)
        intensity = intelligence.calculate_intensity(text)
        
        # Results Section
        st.markdown("### Analysis Result")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="stat-card"><h4>Type</h4></div>', unsafe_allow_html=True)
            type_emoji = {'task': '✓', 'worry': '⚠️', 'idea': '💡'}
            st.markdown(f'<div style="text-align: center; margin-top: -60px; padding: 20px;"><span style="font-size: 2rem;">{type_emoji.get(classification["type"], "•")}</span><br><strong>{classification["type"].upper()}</strong></div>', unsafe_allow_html=True)
        
        with col2:
            conf_pct = round(classification['confidence'] * 100)
            conf_color = 'confidence-high' if conf_pct >= 80 else 'confidence-medium' if conf_pct >= 60 else 'confidence-low'
            st.markdown('<div class="stat-card"><h4>Confidence</h4></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align: center; margin-top: -60px; padding: 20px;"><span class="{conf_color}" style="font-size: 2rem;">{conf_pct}%</span></div>', unsafe_allow_html=True)
        
        with col3:
            intensity_color = f'intensity-{intensity}'
            st.markdown('<div class="stat-card"><h4>Intensity</h4></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align: center; margin-top: -60px; padding: 20px;"><span class="{intensity_color}" style="font-size: 2rem;">{intensity}/10</span></div>', unsafe_allow_html=True)
        
        with col4:
            default_status = {'task': 'pending', 'worry': 'active', 'idea': 'raw'}
            st.markdown('<div class="stat-card"><h4>Status</h4></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align: center; margin-top: -60px; padding: 20px;"><strong>{default_status[classification["type"]]}</strong></div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Details
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**Why this classification?**")
            st.markdown(f"> {classification['reasoning']}")
        
        with col2:
            st.markdown("**Alternative Classifications**")
            if classification['alternatives']:
                for alt in classification['alternatives']:
                    pct = round(alt['confidence'] * 100)
                    st.markdown(f"• **{alt['type'].upper()}**: {pct}%")
            else:
                st.markdown("No strong alternatives")
        
        st.divider()
        
        # Save Button
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("💾 Save This Thought", use_container_width=True, type="primary"):
                thought = create_thought_object(text, classification, intensity)
                st.session_state.thoughts.append(thought)
                save_thoughts_data(st.session_state.thoughts)
                
                st.success(f"✓ Saved as {classification['type'].upper()}!")
                st.balloons()
                st.rerun()


# ============================================================================
# PAGE: ALL THOUGHTS
# ============================================================================

elif page == "📚 All Thoughts":
    st.markdown('<p class="hero-title">Your Thoughts</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Complete history of everything on your mind</p>', unsafe_allow_html=True)
    
    thoughts = st.session_state.thoughts
    
    if not thoughts:
        st.info("📝 No thoughts yet. Start by adding one!")
    else:
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            type_filter = st.multiselect(
                "Type",
                ['task', 'worry', 'idea'],
                default=['task', 'worry', 'idea'],
                key="type_filter"
            )
        
        with col2:
            status_filter = st.multiselect(
                "Status",
                ['pending', 'in-progress', 'done', 'active', 'managed', 'resolved', 'raw', 'refined', 'archived'],
                default=['pending', 'in-progress', 'active', 'raw'],
                key="status_filter"
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sort",
                ["Newest", "Oldest", "Highest Intensity", "Lowest Intensity"]
            )
        
        # Filter and sort
        filtered = [t for t in thoughts if t['type'] in type_filter and t['status'] in status_filter]
        
        if sort_by == "Newest":
            filtered.sort(key=lambda x: x['created'], reverse=True)
        elif sort_by == "Oldest":
            filtered.sort(key=lambda x: x['created'])
        elif sort_by == "Highest Intensity":
            filtered.sort(key=lambda x: x['intensity'], reverse=True)
        else:
            filtered.sort(key=lambda x: x['intensity'])
        
        st.markdown(f"**Showing {len(filtered)} of {len(thoughts)} thoughts**")
        st.divider()
        
        # Display thoughts
        for i, thought in enumerate(filtered):
            col1, col2 = st.columns([0.15, 0.85])
            
            with col1:
                new_status = st.selectbox(
                    "Status",
                    ["pending", "in-progress", "done"] if thought['type'] == 'task'
                    else ["active", "managed", "resolved"] if thought['type'] == 'worry'
                    else ["raw", "refined", "archived"],
                    index=0,
                    key=f"status_{thought['id']}_{i}",
                    label_visibility="collapsed"
                )
                
                if new_status != thought['status']:
                    idx = st.session_state.thoughts.index(thought)
                    st.session_state.thoughts[idx]['status'] = new_status
                    save_thoughts_data(st.session_state.thoughts)
                    st.rerun()
            
            with col2:
                type_emoji = {'task': '✓', 'worry': '⚠️', 'idea': '💡'}
                type_badge = f'<span class="badge badge-{thought["type"]}">{type_emoji.get(thought["type"], "•")} {thought["type"].upper()}</span>'
                
                intensity_class = f'intensity-{thought["intensity"]}'
                confidence_class = 'confidence-high' if thought['confidence'] >= 0.8 else 'confidence-medium' if thought['confidence'] >= 0.6 else 'confidence-low'
                
                st.markdown(f"""
                <div class="thought-card {thought['type']}">
                    <div style="margin-bottom: 12px;">
                        {type_badge}
                        <span class="badge" style="background: rgba(59, 130, 246, 0.15); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.3); margin-left: 8px;">📊 {round(thought['confidence']*100)}%</span>
                        <span class="badge" style="margin-left: 8px;"><span class="{intensity_class}">● {thought['intensity']}/10</span></span>
                    </div>
                    <p style="margin: 12px 0; color: var(--text-primary); line-height: 1.6;">{thought['text']}</p>
                    <small style="color: var(--text-secondary);">📅 {thought['created'][:10]}</small>
                </div>
                """, unsafe_allow_html=True)


# ============================================================================
# PAGE: ANALYSIS
# ============================================================================

elif page == "📊 Analysis":
    st.markdown('<p class="hero-title">Pattern Analysis</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Understand your thinking patterns</p>', unsafe_allow_html=True)
    
    thoughts = st.session_state.thoughts
    intelligence = st.session_state.intelligence
    
    if not thoughts:
        st.info("📝 No thoughts to analyze yet.")
    else:
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Thoughts", len(thoughts))
        
        with col2:
            avg_intensity = sum(t['intensity'] for t in thoughts) / len(thoughts)
            st.metric("Avg Intensity", f"{avg_intensity:.1f}/10")
        
        with col3:
            completed = sum(1 for t in thoughts if t['status'] == 'done')
            st.metric("Completed", completed)
        
        with col4:
            duplicates = len(intelligence.find_similar_thoughts(thoughts))
            st.metric("Duplicates", duplicates)
        
        st.divider()
        
        # Analysis
        patterns = intelligence.analyze_patterns(thoughts)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**Type Breakdown**")
            if patterns['type_breakdown']:
                for t_type, count in patterns['type_breakdown'].items():
                    pct = (count / patterns['total']) * 100
                    st.markdown(f"• **{t_type.upper()}**: {count} ({pct:.0f}%)")
        
        with col2:
            st.markdown("**Avg Intensity by Type**")
            if patterns['avg_intensity_by_type']:
                for t_type, avg in patterns['avg_intensity_by_type'].items():
                    st.markdown(f"• **{t_type.upper()}**: {avg}/10")
        
        st.divider()
        
        st.markdown("**Top Topics**")
        if patterns['top_keywords']:
            cols = st.columns(min(5, len(patterns['top_keywords'])))
            for i, (keyword, count) in enumerate(patterns['top_keywords']):
                with cols[i]:
                    st.metric(keyword.title(), count)


# ============================================================================
# PAGE: RECOMMENDATION
# ============================================================================

elif page == "🎯 Recommendation":
    st.markdown('<p class="hero-title">Next Action</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">What should you focus on now?</p>', unsafe_allow_html=True)
    
    thoughts = st.session_state.thoughts
    intelligence = st.session_state.intelligence
    
    if not thoughts:
        st.info("📝 No thoughts to recommend.")
    else:
        recommendation = intelligence.get_next_action(thoughts)
        
        if not recommendation['has_recommendation']:
            st.success(f"✓ {recommendation['message']}")
            st.balloons()
        else:
            action = recommendation['top_action']
            
            st.markdown("### Recommended Action")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**{action['text']}**")
            
            with col2:
                st.metric("Type", action['type'].upper())
            
            with col3:
                st.metric("Priority", f"{recommendation['score']:.1%}")
            
            st.divider()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Intensity", f"{action['intensity']}/10")
            
            with col2:
                created = datetime.fromisoformat(action['created'])
                age = (datetime.now() - created).days
                st.metric("Age", f"{age}d ago")
            
            with col3:
                st.metric("Status", action['status'])


# ============================================================================
# FOOTER
# ============================================================================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Data**")
    st.markdown(f"Thoughts saved: `axon_thoughts.json`")

with col2:
    st.markdown("**Status**")
    st.markdown("✓ All systems operational")

with col3:
    st.markdown("**About**")
    st.markdown("Axon Intelligence v3")

st.markdown("""
<div style="text-align: center; color: var(--text-secondary); font-size: 0.9em; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--border-color);">
<p>🧠 <strong>Axon Intelligence</strong></p>
<p>Advanced thought organization • Local • Private • Intelligent</p>
</div>
""", unsafe_allow_html=True)