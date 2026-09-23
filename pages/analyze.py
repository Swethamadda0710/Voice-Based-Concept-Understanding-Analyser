import os
import streamlit as st

try:
    from streamlit_mic_recorder import mic_recorder
except ModuleNotFoundError:
    mic_recorder = None


SUBJECTS = ["Artificial Intelligence", "Operating System", "DBMS", "Computer Networks", "Machine Learning", "Java", "Python", "Other"]


def render_analyze():
    st.markdown("<div class='eyebrow'>VOICE ANALYSIS STUDIO</div><h1>Analyze a <em>student response.</em></h1><p class='muted'>Give the AI a reference answer, then upload or record the response you want to understand.</p>", unsafe_allow_html=True)
    st.markdown("<div class='card-label'>01 / CONTEXT</div><h2>Set the evaluation brief</h2>", unsafe_allow_html=True)
    reference_answer = st.text_area("Reference answer", height=150, placeholder="Paste the ideal answer or key concepts students should cover...")
    one, two = st.columns(2)
    with one:
        student_name = st.text_input("Student name *", placeholder="e.g. Ananya Rao")
        subject = st.selectbox("Subject", SUBJECTS)
    with two:
        roll_number = st.text_input("Roll number *", placeholder="e.g. CS-042")
        section = st.text_input("Section", placeholder="e.g. A")
    st.markdown("<div class='card-label audio-label'>02 / AUDIO INPUT</div><h2>Bring in a voice</h2><p class='muted'>MP3, WAV, or MPEG, up to 200 MB</p>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload audio", type=["mp3", "wav", "mpeg", "mpg"], label_visibility="collapsed")
    if mic_recorder is not None:
        st.markdown("<div class='or-divider'><span>or record directly</span></div>", unsafe_allow_html=True)
        recorded_audio = mic_recorder(start_prompt="◉  Start recording", stop_prompt="■  Stop recording", key="conceptlens_recorder")
    else:
        recorded_audio = None
        st.info("Live recording is unavailable in this environment. Install streamlit-mic-recorder to enable it; audio upload is ready to use.")
    audio_path = None
    if uploaded_file is not None or recorded_audio:
        os.makedirs("audio", exist_ok=True)
        if uploaded_file is not None:
            audio_path = os.path.join("audio", uploaded_file.name)
            with open(audio_path, "wb") as audio_file:
                audio_file.write(uploaded_file.getvalue())
        elif recorded_audio and recorded_audio.get("bytes"):
            audio_path = os.path.join("audio", "recorded_audio.wav")
            with open(audio_path, "wb") as audio_file:
                audio_file.write(recorded_audio["bytes"])
        if audio_path:
            st.audio(audio_path)
    if st.button("Run AI analysis  ✦", type="primary", use_container_width=True, disabled=audio_path is None):
        if not student_name.strip() or not roll_number.strip() or not reference_answer.strip():
            st.error("Student name, roll number, and reference answer are required.")
            return
        with st.status("Analyzing voice with ConceptLens AI...", expanded=True) as status:
            from modules.audio_features import extract_audio_features, plot_waveform
            from modules.pdf_report import generate_pdf
            from modules.scoring import calculate_score
            from modules.semantic_analysis import calculate_similarity
            from modules.speech_to_text import transcribe_audio
            from modules.history import save_result
            st.write("Transcribing the response with Whisper...")
            transcript = transcribe_audio(audio_path)
            if not transcript.strip():
                status.update(label="No speech detected", state="error")
                st.error("Speech could not be recognized. Please try a clearer recording.")
                return
            st.write("Comparing meaning and measuring delivery...")
            similarity = calculate_similarity(reference_answer, transcript)
            features = extract_audio_features(audio_path, transcript)
            final_score, feedback = calculate_score(similarity, features)
            save_result(student_name, roll_number, subject, similarity, final_score, feedback)
            os.makedirs("reports", exist_ok=True)
            pdf_path = generate_pdf(student_name=student_name, roll_number=roll_number, subject=subject, section=section, transcript=transcript, similarity=similarity, features=features, final_score=final_score, feedback=feedback, output_path=f"reports/{roll_number}_Concept_Report.pdf")
            waveform_path = plot_waveform(audio_path)
            status.update(label="Analysis complete", state="complete")
        st.session_state.last_result = {"student_name": student_name, "roll_number": roll_number, "subject": subject, "transcript": transcript, "similarity": similarity, "features": features, "final_score": final_score, "feedback": feedback, "pdf_path": pdf_path, "waveform_path": waveform_path}
    result = st.session_state.get("last_result")
    if result:
        st.markdown("<div class='section-heading'><div><div class='eyebrow'>03 / INSIGHT REPORT</div><h2>Here is what we heard</h2></div><span class='status-pill'>● ANALYSIS COMPLETE</span></div>", unsafe_allow_html=True)
        one, two = st.columns([1.15, 0.85])
        with one:
            st.markdown(f"<div class='glass-card transcript-card'><div class='card-label'>TRANSCRIPTION</div><p>{result['transcript']}</p></div>", unsafe_allow_html=True)
            st.image(result["waveform_path"], use_container_width=True)
        with two:
            score = min(max(result["similarity"], 0), 100)
            st.markdown(f"<div class='score-card'><div class='score-ring' style='--score:{score * 3.6}deg'><strong>{score:.1f}<small>%</small></strong></div><div class='card-label'>SEMANTIC SIMILARITY</div><p>{result['feedback']}</p></div>", unsafe_allow_html=True)
            metric_cols = st.columns(2)
            for column, label, value in zip(metric_cols * 2, ["Accuracy", "Precision", "Recall", "F1 Score"], [result["final_score"], result["features"]["speech_rate"], result["features"]["energy"], result["features"]["duration"]]):
                with column:
                    st.metric(label, f"{value:.1f}" if isinstance(value, float) else value)
            with open(result["pdf_path"], "rb") as pdf_file:
                st.download_button("Download PDF report  ↓", pdf_file, file_name=f"{result['roll_number']}_Concept_Report.pdf", mime="application/pdf", use_container_width=True)