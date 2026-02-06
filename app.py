import streamlit as st
import json
from datetime import datetime
from collections import Counter
import re

# ============================================================================
# CORE: IMPORTANCE SCORING
# ============================================================================

def score_importance(thought):
    """
    Score thought importance (0-10) based on:
    - Emotional intensity (capitals, exclamation, worried, excited)
    - Action urgency (deadline, asap, must, need, today)
    - Time sensitivity (today, tomorrow, deadline, by)
    - Repeated mentions (same topic appears multiple times)
    """
    score = 0
    thought_lower = thought.lower()
    
    # EMOTIONAL INTENSITY
    if any(char.isupper() for char in thought) and len(thought) > 10:
        caps_ratio = sum(1 for c in thought if c.isupper()) / len(thought)
        if caps_ratio > 0.3:  # More than 30% caps
            score += 3
        elif caps_ratio > 0.1:  # More than 10% caps
            score += 1
    
    if thought.count('!') > 0:
        score += 2
    
    if thought.count('?') > 1:
        score += 1
    
    # EMOTIONAL WORDS
    intense_words = ['stressed', 'worried', 'anxious', 'terrified', 'love', 'hate', 'amazing', 'terrible', 'urgent', 'critical']
    for word in intense_words:
        if word in thought_lower:
            score += 2
    
    # URGENCY MARKERS
    urgency_words = ['asap', 'today', 'now', 'must', 'need to', 'deadline', 'by tomorrow', 'immediately', 'emergency']
    for word in urgency_words:
        if word in thought_lower:
            score += 3
    
    # TIME SENSITIVITY
    time_words = ['today', 'tomorrow', 'tonight', 'this week', 'deadline', 'by friday', 'by sunday']
    for word in time_words:
        if word in thought_lower:
            score += 2
    
    # PREVENT OVERFLOW
    return min(score, 10)


def extract_themes(thoughts):
    """
    Find what you actually care about most.
    Returns frequency of key topics.
    """
    themes = Counter()
    
    # Extract key words (nouns, actionable words)
    important_words = [
        'project', 'work', 'family', 'health', 'money', 'school',
        'relationship', 'car', 'house', 'code', 'app', 'feature',
        'meeting', 'deadline', 'exam', 'interview', 'presentation',
        'goal', 'dream', 'career', 'fitness', 'anxiety', 'stress'
    ]
    
    for thought in thoughts:
        thought_lower = thought.lower()
        for word in important_words:
            if word in thought_lower:
                themes[word] += 1
    
    return themes.most_common(5)


# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Axon - Brain Dump Organizer",
    page_icon="🧠",
    layout="wide"
)

st.markdown("""
    <style>
    /* Color Palette */
    :root {
        --primary: #2563eb;
        --critical: #dc2626;
        --high: #ea580c;
        --medium: #6366f1;
        --low: #8b5cf6;
        --dark: #1e293b;
        --light: #f8fafc;
    }
    
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
    }
    
    /* Main background */
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    .main-title {
        font-size: 2.8em;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 8px 0;
        letter-spacing: -1px;
    }
    
    .subtitle {
        font-size: 1.05em;
        color: #cbd5e1;
        margin-bottom: 30px;
        font-weight: 400;
        letter-spacing: 0.3px;
    }
    
    /* CRITICAL - Deep Red */
    .thought-critical {
        background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
        border-left: 6px solid #ef4444;
        padding: 16px 18px;
        border-radius: 8px;
        margin: 10px 0;
        color: #fecaca;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.15);
        transition: all 0.2s ease;
    }
    
    .thought-critical:hover {
        background: linear-gradient(135deg, #8f2020 0%, #a21a1a 100%);
        box-shadow: 0 6px 16px rgba(239, 68, 68, 0.25);
    }
    
    /* HIGH - Orange */
    .thought-high {
        background: linear-gradient(135deg, #7c2d12 0%, #92400e 100%);
        border-left: 6px solid #fb923c;
        padding: 16px 18px;
        border-radius: 8px;
        margin: 10px 0;
        color: #fed7aa;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(251, 146, 60, 0.15);
        transition: all 0.2s ease;
    }
    
    .thought-high:hover {
        background: linear-gradient(135deg, #8b3617 0%, #a03f1b 100%);
        box-shadow: 0 6px 16px rgba(251, 146, 60, 0.25);
    }
    
    /* MEDIUM - Indigo */
    .thought-medium {
        background: linear-gradient(135deg, #3730a3 0%, #4c1d95 100%);
        border-left: 6px solid #818cf8;
        padding: 16px 18px;
        border-radius: 8px;
        margin: 10px 0;
        color: #c7d2fe;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(129, 140, 248, 0.15);
        transition: all 0.2s ease;
    }
    
    .thought-medium:hover {
        background: linear-gradient(135deg, #3f3cb3 0%, #5f2aa5 100%);
        box-shadow: 0 6px 16px rgba(129, 140, 248, 0.25);
    }
    
    /* LOW - Purple */
    .thought-low {
        background: linear-gradient(135deg, #4c1d95 0%, #581c87 100%);
        border-left: 6px solid #a78bfa;
        padding: 16px 18px;
        border-radius: 8px;
        margin: 10px 0;
        color: #ddd6fe;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(167, 139, 250, 0.15);
        transition: all 0.2s ease;
    }
    
    .thought-low:hover {
        background: linear-gradient(135deg, #552ca8 0%, #6d2d8f 100%);
        box-shadow: 0 6px 16px rgba(167, 139, 250, 0.25);
    }
    
    .score-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.15);
        padding: 4px 10px;
        border-radius: 14px;
        font-size: 0.8em;
        margin-left: 8px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    /* Pattern Box */
    .pattern-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
        border: 2px solid #3b82f6;
        padding: 20px;
        border-radius: 10px;
        margin: 16px 0;
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.15);
    }
    
    .pattern-title {
        font-weight: 700;
        color: #93c5fd;
        margin-bottom: 12px;
        font-size: 1.1em;
        letter-spacing: 0.5px;
    }
    
    .pattern-item {
        font-size: 0.95em;
        color: #bfdbfe;
        margin: 8px 0;
        padding: 6px 0;
        border-bottom: 1px solid rgba(191, 219, 254, 0.2);
    }
    
    .pattern-item:last-child {
        border-bottom: none;
    }
    
    /* Section Headers */
    h3 {
        color: #f1f5f9;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-top: 28px;
        margin-bottom: 16px;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 6px;
        color: #93c5fd;
        font-size: 0.95em;
    }
    
    /* Divider */
    hr {
        border-color: #334155;
    }
    
    /* Streamlit stMetric */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# UI LAYOUT
# ============================================================================

st.markdown('<div class="main-title">🧠 Axon</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Dump everything. See it organized. Understand what you actually care about.</div>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📝 Brain Dump")
    user_input = st.text_area(
        "Type anything and everything on your mind.",
        placeholder="No structure needed. Just get it out.",
        height=200,
        label_visibility="collapsed"
    )

with col2:
    st.subheader("How it works")
    st.info("""
    1. You dump thoughts
    2. Axon organizes them
    3. Color shows importance
    4. Patterns show what matters
    """)

# ============================================================================
# PROCESS
# ============================================================================

if st.button("Organize", type="primary", use_container_width=True):
    if user_input.strip():
        # Split into individual thoughts (sentences/lines)
        thoughts = [t.strip() for t in re.split(r'[\n.!?]+', user_input.strip()) if t.strip()]
        
        # Score each thought
        scored_thoughts = [(t, score_importance(t)) for t in thoughts]
        
        # Sort by importance (highest first)
        scored_thoughts.sort(key=lambda x: x[1], reverse=True)
        
        # Store in session
        st.session_state.scored_thoughts = scored_thoughts
        st.session_state.original_thoughts = thoughts
        st.success(f"✓ Organized {len(thoughts)} thoughts")
    else:
        st.warning("Please enter some thoughts first")


# ============================================================================
# DISPLAY ORGANIZED THOUGHTS
# ============================================================================

if 'scored_thoughts' in st.session_state:
    scored_thoughts = st.session_state.scored_thoughts
    original_thoughts = st.session_state.original_thoughts
    
    st.divider()
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_importance = sum(s[1] for s in scored_thoughts) / len(scored_thoughts) if scored_thoughts else 0
        st.metric("Average Importance", f"{avg_importance:.1f}/10")
    with col2:
        critical_count = sum(1 for _, score in scored_thoughts if score >= 8)
        st.metric("Critical Thoughts", critical_count)
    with col3:
        st.metric("Total Thoughts", len(scored_thoughts))
    
    st.divider()
    
    # Organize by importance level
    critical = [t for t, s in scored_thoughts if s >= 8]
    high = [t for t, s in scored_thoughts if 6 <= s < 8]
    medium = [t for t, s in scored_thoughts if 4 <= s < 6]
    low = [t for t, s in scored_thoughts if s < 4]
    
    # Display by importance tier
    st.markdown("### 🔴 Critical (8-10)")
    if critical:
        for thought in critical:
            score = score_importance(thought)
            display_text = thought.replace('<', '&lt;').replace('>', '&gt;')
            st.markdown(f'<div class="thought-critical">{display_text}<span class="score-badge">{score}</span></div>', 
                       unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">✓ No critical thoughts right now</div>', unsafe_allow_html=True)
    
    st.markdown("### 🟠 High Priority (6-7)")
    if high:
        for thought in high:
            score = score_importance(thought)
            display_text = thought.replace('<', '&lt;').replace('>', '&gt;')
            st.markdown(f'<div class="thought-high">{display_text}<span class="score-badge">{score}</span></div>', 
                       unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">✓ No high-priority thoughts</div>', unsafe_allow_html=True)
    
    st.markdown("### 🔵 Medium Priority (4-5)")
    if medium:
        for thought in medium:
            score = score_importance(thought)
            display_text = thought.replace('<', '&lt;').replace('>', '&gt;')
            st.markdown(f'<div class="thought-medium">{display_text}<span class="score-badge">{score}</span></div>', 
                       unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">✓ No medium-priority thoughts</div>', unsafe_allow_html=True)
    
    st.markdown("### 🟣 Low Priority (0-3)")
    if low:
        with st.expander(f"Show {len(low)} low-priority thoughts"):
            for thought in low:
                score = score_importance(thought)
                display_text = thought.replace('<', '&lt;').replace('>', '&gt;')
                st.markdown(f'<div class="thought-low">{display_text}<span class="score-badge">{score}</span></div>', 
                           unsafe_allow_html=True)
    
    # PATTERN DETECTION
    st.divider()
    st.markdown("### 📊 What You Actually Care About")
    
    themes = extract_themes(original_thoughts)
    if themes:
        st.markdown('<div class="pattern-box">', unsafe_allow_html=True)
        st.markdown('<div class="pattern-title">Your Top Concerns:</div>', unsafe_allow_html=True)
        
        for theme, count in themes:
            percentage = (count / len(original_thoughts)) * 100
            bar_width = int(percentage / 2)
            bar = "█" * bar_width + "░" * (50 - bar_width)
            st.markdown(f'<div class="pattern-item"><strong>{theme.upper()}</strong> {bar} {percentage:.0f}% ({count}x)</div>', 
                       unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Insight
        top_theme = themes[0][0] if themes else "everything"
        st.info(f"💡 **{top_theme.upper()}** is what's dominating your thinking. This is what actually matters to you right now.")
    
    st.divider()
    
    if st.button("Clear & Start Over", use_container_width=True):
        st.session_state.clear()
        st.rerun()