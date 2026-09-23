import os
from datetime import datetime

import streamlit as st

from modules import portal_db


SUBJECTS = ["Artificial Intelligence", "Operating System", "DBMS", "Computer Networks", "Machine Learning", "Java", "Python", "Other"]


def _user():
    return st.session_state["user"]


def _profile():
    return portal_db.profile_for_user(_user()["id"], "student")


def _metric(label, value, icon, accent=""):
    return f"<div class='metric-card {accent}'><div class='metric-icon'>{icon}</div><strong>{value}</strong><span>{label}</span></div>"


def render_student_portal(page):
    profile = _profile()
    assignments = portal_db.assignments_for_student(_user()["id"])
    results = portal_db.submissions_for_student(_user()["id"])
    if page == "Dashboard":
        _dashboard(profile, assignments, results)
    elif page == "My Assignments":
        _assignments(assignments)
    elif page == "Submit Answer":
        _submit_answer(assignments)
    elif page == "My Results":
        _results(results)
    else:
        _profile_page(profile)


def _dashboard(profile, assignments, results):
    st.markdown("<div class='eyebrow'>STUDENT PORTAL</div><h1>Welcome, <em>" + (profile.get("name") or profile["username"]) + ".</em></h1><p class='muted'>Your assigned concepts and understanding progress.</p>", unsafe_allow_html=True)
    completed = len(results)
    pending = len([item for item in assignments if item["status"] != "Completed"])
    average = round(sum(item["final_score"] for item in results) / completed, 1) if completed else 0
    columns = st.columns(4)
    for column, markup in zip(columns, [_metric("Assigned Questions", len(assignments), "◌"), _metric("Completed Questions", completed, "✓", "blue"), _metric("Pending Questions", pending, "◷", "pink"), _metric("Average Understanding", f"{average}%", "↗", "green")]):
        with column:
            st.markdown(markup, unsafe_allow_html=True)
    st.markdown("<div class='section-heading'><div><div class='eyebrow'>YOUR WORK</div><h2>Assigned Questions</h2></div></div>", unsafe_allow_html=True)
    _assignment_rows(assignments[:6])


def _assignment_rows(assignments):
    if not assignments:
        st.info("No approved questions have been assigned to you yet.")
        return
    for assignment in assignments:
        with st.container():
            status = assignment["status"]
            st.markdown(f"<div class='report-row'><div class='report-avatar'>?</div><div class='report-main'><b>{assignment['question_text']}</b><span>{assignment['concept']} · Teacher: {assignment['teacher_name']}</span></div><div class='report-score'><strong>{status}</strong><small>{assignment.get('due_date') or 'No due date'}</small></div></div>", unsafe_allow_html=True)
            button = "View Result" if status == "Completed" else ("Continue" if status == "In Progress" else "Answer Now")
            if st.button(button, key=f"student_assignment_{assignment['id']}"):
                st.session_state.selected_assignment = assignment["id"]
                st.session_state.active_page = "My Results" if status == "Completed" else "Submit Answer"
                st.rerun()


def _assignments(assignments):
    st.markdown("<div class='eyebrow'>STUDENT PORTAL</div><h1>My <em>assignments.</em></h1><p class='muted'>Only questions assigned to your account appear here.</p>", unsafe_allow_html=True)
    _assignment_rows(assignments)


def _submit_answer(assignments):
    profile = _profile()
    assignment_id = st.session_state.get("selected_assignment")
    assignment = next((item for item in assignments if item["id"] == assignment_id), None)
    if assignment is None and assignments:
        assignment = assignments[0]
        assignment_id = assignment["id"]
    st.markdown("<div class='eyebrow'>ANSWER SUBMISSION</div><h1>Explain the <em>concept.</em></h1>", unsafe_allow_html=True)
    if assignment is None:
        st.info("Choose an approved assignment before submitting an answer.")
        return
    st.markdown(f"<div class='glass-card'><div class='card-label'>QUESTION</div><h2>{assignment['question_text']}</h2><p class='muted'>{assignment['concept']} · {assignment['subject']}</p><p>Explain the concept clearly in your own words. You may record an answer or upload an audio file.</p></div>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload audio answer", type=["wav", "mp3", "m4a", "ogg", "mpeg"], key=f"upload_{assignment_id}")
    recorded = None
    try:
        from streamlit_mic_recorder import mic_recorder
        recorded = mic_recorder(start_prompt="◉  Start recording", stop_prompt="■  Stop recording", key=f"recorder_{assignment_id}")
    except ModuleNotFoundError:
        st.caption("Recording is unavailable in this environment. Upload an audio file instead.")
    audio_path = None
    if uploaded:
        if uploaded.size > 200 * 1024 * 1024:
            st.error("Audio files must be smaller than 200 MB.")
            return
        os.makedirs(os.path.join("uploads", "students", str(_user()["id"])), exist_ok=True)
        audio_path = os.path.join("uploads", "students", str(_user()["id"]), os.path.basename(uploaded.name))
        with open(audio_path, "wb") as audio_file:
            audio_file.write(uploaded.getvalue())
    elif recorded and recorded.get("bytes"):
        os.makedirs(os.path.join("uploads", "students", str(_user()["id"])), exist_ok=True)
        audio_path = os.path.join("uploads", "students", str(_user()["id"]), f"assignment_{assignment_id}.wav")
        with open(audio_path, "wb") as audio_file:
            audio_file.write(recorded["bytes"])
    if audio_path:
        st.audio(audio_path)
    if st.button("Submit Answer  ✦", type="primary", use_container_width=True, disabled=audio_path is None):
        with st.status("Processing your answer...", expanded=True) as status:
            from modules.audio_features import extract_audio_features
            from modules.pdf_report import generate_pdf
            from modules.scoring import calculate_score
            from modules.semantic_analysis import calculate_similarity
            from modules.speech_to_text import transcribe_audio
            st.write("Converting speech to text with Whisper...")
            transcript = transcribe_audio(audio_path)
            if not transcript.strip():
                status.update(label="No speech detected", state="error")
                return
            st.write("Analyzing semantic meaning and audio delivery...")
            similarity = calculate_similarity(assignment["reference_answer"], transcript)
            features = extract_audio_features(audio_path, transcript)
            final_score, feedback = calculate_score(similarity, features)
            submission_id = portal_db.save_submission(_user()["id"], assignment_id, audio_path, transcript, similarity, final_score, feedback, feedback)
            if not submission_id:
                status.update(label="Submission was not authorized", state="error")
                return
            pdf_path = generate_pdf(profile_name(), profile["student_id"], assignment["subject"], profile.get("section", ""), transcript, similarity, features, final_score, feedback, f"reports/submission_{submission_id}.pdf")
            status.update(label="Answer evaluated and saved", state="complete")
        st.session_state.selected_submission = submission_id
        st.session_state.active_page = "My Results"
        st.rerun()


def profile_name():
    return _profile().get("name") or _user()["username"]


def _results(results):
    st.markdown("<div class='eyebrow'>STUDENT PORTAL</div><h1>My <em>results.</em></h1><p class='muted'>Your submissions, scores, and generated reports.</p>", unsafe_allow_html=True)
    if not results:
        st.info("Completed evaluations will appear here.")
        return
    for result in results:
        st.markdown(f"<div class='report-row'><div class='report-avatar'>{result['final_score']:.0f}</div><div class='report-main'><b>{result['question_text']}</b><span>{result['concept']} · {result['submitted_at']}</span></div><div class='report-score'><strong>{result['final_score']:.1f}%</strong><small>{result['understanding_level']}</small></div></div>", unsafe_allow_html=True)
        if st.button("View Detailed Result", key=f"result_{result['id']}"):
            st.session_state.selected_submission = result["id"]
        if st.session_state.get("selected_submission") == result["id"]:
            st.markdown(f"<div class='glass-card transcript-card'><div class='card-label'>TRANSCRIPTION</div><p>{result['transcription']}</p><div class='card-label'>UNDERSTANDING SCORE</div><h2>{result['final_score']:.2f}%</h2><p>{result['understanding_level']}</p></div>", unsafe_allow_html=True)
            report_path = f"reports/submission_{result['id']}.pdf"
            if os.path.exists(report_path):
                with open(report_path, "rb") as report_file:
                    st.download_button("Download PDF report  ↓", report_file, file_name=os.path.basename(report_path), mime="application/pdf", key=f"download_{result['id']}")


def _profile_page(profile):
    st.markdown("<div class='eyebrow'>STUDENT PORTAL</div><h1>My <em>profile.</em></h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='profile-card'><div class='avatar huge'>{profile.get('name', 'S')[:1].upper()}</div><h2>{profile.get('name') or profile['username']}</h2><p class='muted'>Student account</p><div class='profile-line'>Student ID <span>{profile.get('student_id', 'Not set')}</span></div><div class='profile-line'>Email <span>{profile.get('email') or 'Not set'}</span></div><div class='profile-line'>Class / section <span>{profile.get('class_name') or 'Not set'} / {profile.get('section') or 'Not set'}</span></div></div>", unsafe_allow_html=True)
