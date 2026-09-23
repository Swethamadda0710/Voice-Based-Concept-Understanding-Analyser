import os
import streamlit as st
from modules.dashboard import get_dashboard_data


def render_home():
    try:
        dashboard = get_dashboard_data()
    except (FileNotFoundError, KeyError):
        dashboard = {"total": 0, "average": 0, "highest": 0, "strong": 0, "moderate": 0, "weak": 0}
    st.markdown("<div class='topline'><div><div class='eyebrow'>CONCEPTLENS AI WORKSPACE</div><h1>Welcome to <em>ConceptLens AI.</em></h1><p class='muted'>Voice Based Concept Understanding Analyser</p></div><div class='status-pill'>● SYSTEMS OPERATIONAL</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-banner'><div><span class='eyebrow'>AI-POWERED LEARNING INSIGHT</span><h2>Welcome to<br><em>ConceptLens AI.</em></h2><p>Transform voice into conceptual understanding using Artificial Intelligence.</p></div><div class='hero-icon'>🎙️</div></div>", unsafe_allow_html=True)
    if st.button("Start an analysis  →", key="home_analyze", type="primary"):
        st.session_state.active_page = "Analyze Voice"
        st.rerun()
    st.markdown("<div class='section-heading'><div><div class='eyebrow'>YOUR OVERVIEW</div><h2>Workspace pulse</h2></div><span class='muted'>All time</span></div>", unsafe_allow_html=True)
    cols = st.columns(4)
    for column, icon, value, label, accent in zip(cols, ["◌", "↗", "✦", "◍"], [dashboard["total"], f"{dashboard['average']}%", f"{dashboard['highest']}%", dashboard["strong"]], ["Total analyses", "Average score", "Highest score", "Strong concepts"], ["violet", "blue", "pink", "green"]):
        with column:
            st.markdown(f"<div class='metric-card {accent}'><div class='metric-icon'>{icon}</div><strong>{value}</strong><span>{label}</span><small>↗  Live from your workspace</small></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-heading'><div><div class='eyebrow'>QUICK ACCESS</div><h2>Pick up where you left off</h2></div></div>", unsafe_allow_html=True)
    a, b, c = st.columns(3)
    for column, icon, title, copy, page in [(a, "◉", "Analyze a voice", "Evaluate a fresh student response.", "Analyze Voice"), (b, "▣", "Review reports", "Compare past understanding scores.", "Reports"), (c, "◇", "Explore the method", "See how the AI pipeline works.", "About Project")]:
        with column:
            st.markdown(f"<div class='quick-card'><div class='quick-icon'>{icon}</div><h3>{title}</h3><p>{copy}</p></div>", unsafe_allow_html=True)
            if st.button("Open →", key=f"quick_{page}"):
                st.session_state.active_page = page
                st.rerun()