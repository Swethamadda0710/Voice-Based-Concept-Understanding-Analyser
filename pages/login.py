import streamlit as st


def render_login(authenticate, create_user):
    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        st.markdown("<div class='login-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='brand-mark login-brand'><span>🎙️◉</span><div><b>ConceptLens AI</b><small>Voice Based Concept Understanding Analyser</small></div></div>", unsafe_allow_html=True)
        st.markdown("<div class='eyebrow'>VOICE INTELLIGENCE PLATFORM</div>", unsafe_allow_html=True)
        st.markdown("<h1 class='login-title'>Understand every<br><em>spoken idea.</em></h1>", unsafe_allow_html=True)
        st.markdown("<p class='login-copy'>Transform student responses into clear, actionable understanding with responsible AI.</p>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Your username")
            password = st.text_input("Password", type="password", placeholder="Your password")
            remember = st.checkbox("Remember me", value=True)
            submitted = st.form_submit_button("Sign in  →", use_container_width=True)
            if submitted:
                if authenticate(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username.strip()
                    st.session_state.remember = remember
                    st.rerun()
                else:
                    st.error("Those credentials do not match our records.")
        with st.expander("New to ConceptLens AI? Create an account"):
            with st.form("signup_form"):
                new_username = st.text_input("New username")
                new_password = st.text_input("New password", type="password")
                if st.form_submit_button("Create account", use_container_width=True):
                    success, message = create_user(new_username, new_password)
                    (st.success if success else st.error)(message)
        st.caption("Demo access: admin / admin123")
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='login-art'><div class='neural-grid'></div><div class='orb orb-one'></div><div class='orb orb-two'></div><div class='mic-illustration'>♬</div><div class='art-caption'><b>Hear the thinking.</b><span>Measure the understanding.</span></div><div class='floating-stat stat-one'>↗ <b>+24%</b><small>clarity detected</small></div><div class='floating-stat stat-two'>◉ <b>94.8</b><small>concept match</small></div></div>", unsafe_allow_html=True)