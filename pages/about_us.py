import streamlit as st


def render_about_us():
    st.markdown("<div class='eyebrow'>THE PEOPLE BEHIND THE PROJECT</div><h1>Built with curiosity,<br><em>shipped with care.</em></h1><p class='muted'>A student-led project exploring what happens when language technology meets meaningful assessment.</p>", unsafe_allow_html=True)
    cols = st.columns(3)
    for column, initials, name in zip(cols, ["S", "D", "M"], ["Swetha", "DivyaTeja", "Mohammad Saad"]):
        with column:
            st.markdown(f"<div class='team-card'><div class='avatar large'>{initials}</div><h3>{name}</h3></div>", unsafe_allow_html=True)
    st.markdown("<div class='contact-strip'><div><div class='eyebrow'>PROJECT GUIDE</div><h3>Department of Computer Science</h3><p class='muted'>Built at your college with guidance from faculty and a belief in practical AI.</p></div><div><div class='eyebrow'>GET IN TOUCH</div><p>hello@conceptlens.ai</p><button>GitHub ↗</button></div></div>", unsafe_allow_html=True)