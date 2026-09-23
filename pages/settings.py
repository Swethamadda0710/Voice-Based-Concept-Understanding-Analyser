import streamlit as st


def render_settings(change_password):
    st.markdown("<div class='eyebrow'>PREFERENCES</div><h1>Make it <em>yours.</em></h1><p class='muted'>Tune your workspace and keep your account secure.</p>", unsafe_allow_html=True)
    left, right = st.columns([1.1, 0.9], gap="large")
    with left:
        st.markdown("<div class='glass-card'><div class='card-label'>APPEARANCE</div><h2>Workspace mood</h2>", unsafe_allow_html=True)
        theme = st.radio("Theme", ["Dark mode", "Light mode"], horizontal=True, label_visibility="collapsed")
        if theme == "Light mode":
            st.info("Light mode preference saved for the next session. The current visual system is optimized for dark mode.")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card'><div class='card-label'>SECURITY</div><h2>Change password</h2>", unsafe_allow_html=True)
        with st.form("change_password"):
            current = st.text_input("Current password", type="password")
            new = st.text_input("New password", type="password")
            confirm = st.text_input("Confirm new password", type="password")
            if st.form_submit_button("Update password", use_container_width=True):
                if new != confirm or len(new) < 6:
                    st.error("Passwords must match and be at least 6 characters.")
                elif change_password(st.session_state.username, current, new):
                    st.success("Password updated successfully.")
                else:
                    st.error("Current password is incorrect.")
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown(f"<div class='profile-card'><div class='avatar huge'>{st.session_state.get('username', 'A')[:1].upper()}</div><div class='eyebrow'>SIGNED IN AS</div><h2>{st.session_state.get('username', 'Analyst')}</h2><p class='muted'>Workspace member</p><div class='profile-line'>SQLite account <span>● Active</span></div><div class='profile-line'>Remember me <span>{'● On' if st.session_state.get('remember', True) else '○ Off'}</span></div></div>", unsafe_allow_html=True)
        if st.button("Log out of this workspace", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()