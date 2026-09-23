import os
import streamlit as st

from modules.auth import authenticate, change_password, create_user
from pages.about_project import render_about_project
from pages.about_us import render_about_us
from pages.analyze import render_analyze
from pages.home import render_home
from pages.login import render_login
from pages.reports import render_reports
from pages.settings import render_settings


st.set_page_config(
    page_title="ConceptLens AI",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

with open(os.path.join("styles", "style.css"), encoding="utf-8") as stylesheet:
    st.markdown(f"<style>{stylesheet.read()}</style>", unsafe_allow_html=True)


def initialize_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "active_page" not in st.session_state:
        st.session_state.active_page = "Home"
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"


def render_sidebar():
    with st.sidebar:
        st.markdown(
            "<div class='brand-mark'><span>🎙️◉</span><div><b>ConceptLens AI</b><small>Voice Based Concept Understanding Analyser</small></div></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='sidebar-rule'></div>", unsafe_allow_html=True)
        st.caption("WORKSPACE")
        items = [
            ("⌂", "Home"),
            ("◉", "Analyze Voice"),
            ("▣", "Reports"),
            ("◇", "About Project"),
            ("✦", "About Us"),
        ]
        for icon, label in items:
            active = st.session_state.active_page == label
            if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True, type="primary" if active else "secondary"):
                st.session_state.active_page = label
                st.rerun()
        st.markdown("<div class='sidebar-spacer'></div>", unsafe_allow_html=True)
        st.caption("ACCOUNT")
        if st.button("⚙  Settings", key="nav_Settings", use_container_width=True):
            st.session_state.active_page = "Settings"
            st.rerun()
        if st.button("⇥  Log out", key="nav_Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.active_page = "Home"
            st.rerun()
        st.markdown(
            f"<div class='profile-chip'><span class='avatar'>{st.session_state.get('username', 'A')[:1].upper()}</span><div><b>{st.session_state.get('username', 'Analyst')}</b><small>Workspace member</small></div></div>",
            unsafe_allow_html=True,
        )


initialize_state()

if not st.session_state.authenticated:
    render_login(authenticate, create_user)
    st.stop()

render_sidebar()
page = st.session_state.active_page
if page == "Home":
    render_home()
elif page == "Analyze Voice":
    render_analyze()
elif page == "Reports":
    render_reports()
elif page == "About Project":
    render_about_project()
elif page == "About Us":
    render_about_us()
elif page == "Settings":
    render_settings(change_password)