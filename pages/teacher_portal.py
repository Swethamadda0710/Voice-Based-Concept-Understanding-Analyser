import streamlit as st

from modules import portal_db


def _user():
    return st.session_state["user"]


def render_teacher_portal(page):
    if page == "Dashboard":
        _dashboard()
    elif page == "Questions":
        _questions()
    elif page == "Students":
        _students()
    elif page == "Assignments":
        _assignments()
    elif page == "Submissions":
        _submissions()
    elif page == "Reports":
        _submissions(reports=True)
    else:
        _profile()


def _dashboard():
    questions = portal_db.teacher_questions(_user()["id"])
    students = portal_db.students_for_teacher(_user()["id"])
    submissions = portal_db.submissions_for_teacher(_user()["id"])
    average = round(sum(item["final_score"] for item in submissions) / len(submissions), 1) if submissions else 0
    st.markdown("<div class='eyebrow'>TEACHER PORTAL</div><h1>Your learning <em>workspace.</em></h1><p class='muted'>Create approved reference answers, assign concepts, and monitor understanding.</p>", unsafe_allow_html=True)
    columns = st.columns(5)
    metrics = [("Total Students", len(students), "◌"), ("Total Questions", len(questions), "?"), ("Total Assignments", sum(item["assigned_count"] for item in questions), "↗"), ("Total Submissions", len(submissions), "✓"), ("Average Score", f"{average}%", "◍")]
    for column, (label, value, icon) in zip(columns, metrics):
        with column:
            st.markdown(f"<div class='metric-card'><div class='metric-icon'>{icon}</div><strong>{value}</strong><span>{label}</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-heading'><div><div class='eyebrow'>RECENT ACTIVITY</div><h2>Recent Submissions</h2></div></div>", unsafe_allow_html=True)
    _submission_rows(submissions[:8])


def _questions():
    questions = portal_db.teacher_questions(_user()["id"])
    st.markdown("<div class='eyebrow'>TEACHER PORTAL</div><h1>Your <em>questions.</em></h1><p class='muted'>Only approved reference answers can be used for student evaluation.</p>", unsafe_allow_html=True)
    with st.expander("Create Question", expanded=not questions):
        question = st.text_area("Question text", placeholder="What is Machine Learning?")
        concept = st.text_input("Concept / topic")
        subject = st.selectbox("Subject", ["Artificial Intelligence", "Machine Learning", "DBMS", "Java", "Python", "Other"])
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Detailed"])
        answer = st.text_area("Reference answer", height=130)
        if st.button("Generate Reference Answer with AI"):
            try:
                from modules.reference_answer import generate_reference_answer
                st.session_state.reference_draft = generate_reference_answer(question, concept, difficulty)
                st.session_state.reference_source = "AI Generated"
            except Exception as error:
                st.error(str(error))
        draft = st.text_area("AI draft for teacher review", value=st.session_state.get("reference_draft", ""), height=150)
        source = st.session_state.get("reference_source", "Teacher Written") if draft else "Teacher Written"
        approved = st.checkbox("I reviewed and approve this reference answer")
        if st.button("Save Approved Question", type="primary", disabled=not approved):
            question_id = portal_db.create_question(_user()["id"], question, concept, subject, difficulty, draft or answer, source, "Approved")
            if question_id:
                st.success("Question saved with an approved reference answer.")
                st.session_state.reference_draft = ""
                st.rerun()
            st.error("Question text and concept are required.")
    for item in questions:
        st.markdown(f"<div class='report-row'><div class='report-avatar'>?</div><div class='report-main'><b>{item['question_text']}</b><span>{item['concept']} · {item['subject']} · {item['assigned_count']} assigned</span></div><div class='report-score'><strong>{item['reference_answer_status']}</strong><small>{item['reference_answer_source']}</small></div></div>", unsafe_allow_html=True)


def _students():
    students = portal_db.students_for_teacher(_user()["id"])
    st.markdown("<div class='eyebrow'>TEACHER PORTAL</div><h1>Your <em>students.</em></h1><p class='muted'>Students visible here are limited to this teacher's authorized assignments.</p>", unsafe_allow_html=True)
    for student in students:
        st.markdown(f"<div class='report-row'><div class='report-avatar'>{student['name'][:1].upper()}</div><div class='report-main'><b>{student['name']}</b><span>{student['student_id']} · {student['email'] or 'No email'}</span></div><div class='report-score'><strong>{student['average_score']:.1f}%</strong><small>{student['completed_count']} completed / {student['assigned_count']} assigned</small></div></div>", unsafe_allow_html=True)


def _assignments():
    questions = portal_db.teacher_questions(_user()["id"])
    students = portal_db.students_for_teacher(_user()["id"])
    st.markdown("<div class='eyebrow'>TEACHER PORTAL</div><h1>Create an <em>assignment.</em></h1>", unsafe_allow_html=True)
    if not questions or not students:
        st.info("Create a question and ensure at least one student account exists before assigning work.")
        return
    question = st.selectbox("Question", questions, format_func=lambda item: item["question_text"])
    all_students_option = {"id": "all", "name": "All students", "student_id": "ALL"}
    student_options = [all_students_option] + students
    student = st.selectbox("Assign to", student_options, format_func=lambda item: "All students" if item["id"] == "all" else f"{item['name']} ({item['student_id']})")
    due_date = st.date_input("Due date", value=None)
    if st.button("Assign Question", type="primary"):
        student_ids = [item["id"] for item in students] if student["id"] == "all" else [student["id"]]
        created = portal_db.assign_question_to_students(_user()["id"], question["id"], student_ids, str(due_date) if due_date else "")
        if created:
            st.success(f"Assignment created for {created} student{'s' if created != 1 else ''}.")
        else:
            st.info("Those students already have this assignment.")


def _submissions(reports=False):
    submissions = portal_db.submissions_for_teacher(_user()["id"])
    st.markdown("<div class='eyebrow'>TEACHER PORTAL</div><h1>Submission <em>results.</em></h1><p class='muted'>Inspect transcriptions, scores, and understanding levels from your students.</p>", unsafe_allow_html=True)
    _submission_rows(submissions)


def _submission_rows(submissions):
    if not submissions:
        st.info("Student submissions will appear here after evaluation.")
        return
    for item in submissions:
        st.markdown(f"<div class='report-row'><div class='report-avatar'>{item['student_name'][:1].upper()}</div><div class='report-main'><b>{item['student_name']}</b><span>{item['question_text']} · {item['submitted_at']}</span></div><div class='report-score'><strong>{item['final_score']:.1f}%</strong><small>{item['understanding_level']}</small></div></div>", unsafe_allow_html=True)
        if st.button("View Transcription", key=f"teacher_submission_{item['id']}"):
            st.session_state.teacher_detail = item["id"]
        if st.session_state.get("teacher_detail") == item["id"]:
            st.markdown(f"<div class='glass-card transcript-card'><div class='card-label'>TRANSCRIPTION</div><p>{item['transcription']}</p><div class='card-label'>FEEDBACK</div><p>{item['feedback']}</p></div>", unsafe_allow_html=True)


def _profile():
    profile = portal_db.profile_for_user(_user()["id"], "teacher")
    st.markdown("<div class='eyebrow'>TEACHER PORTAL</div><h1>My <em>profile.</em></h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='profile-card'><div class='avatar huge'>{profile.get('name', 'T')[:1].upper()}</div><h2>{profile.get('name') or profile['username']}</h2><p class='muted'>Teacher account</p><div class='profile-line'>Teacher ID <span>{profile.get('teacher_id', 'Not set')}</span></div><div class='profile-line'>Email <span>{profile.get('email') or 'Not set'}</span></div><div class='profile-line'>Department <span>{profile.get('department') or 'Not set'}</span></div></div>", unsafe_allow_html=True)
