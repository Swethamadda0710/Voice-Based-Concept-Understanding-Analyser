import streamlit as st
import os
import pandas as pd

from modules.speech_to_text import transcribe_audio
from modules.semantic_analysis import calculate_similarity
from modules.audio_features import (
    extract_audio_features,
    plot_waveform
)
from modules.scoring import calculate_score
from modules.pdf_report import generate_pdf
from modules.history import save_result
import plotly.express as px
from modules.dashboard import get_dashboard_data
from streamlit_mic_recorder import mic_recorder


st.set_page_config(
    page_title="Voice Based Concept Understanding Analyser",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>

.stApp{
    background-color:#f4f8fb;
}

.main-title{
    text-align:center;
    font-size:42px;
    font-weight:bold;
    color:#0F4C81;
}

.sub-title{
    text-align:center;
    font-size:18px;
    color:#555;
    margin-bottom:25px;
}

.card{
    background:white;
    padding:25px;
    border-radius:15px;
    box-shadow:0px 4px 12px rgba(0,0,0,0.12);
    margin-bottom:20px;
}

.stButton>button{
    width:100%;
    height:55px;
    border-radius:12px;
    font-size:18px;
    font-weight:bold;
    background:#0F4C81;
    color:white;
}

[data-testid="stFileUploader"]{
    border:2px dashed #0F4C81;
    border-radius:15px;
    padding:15px;
}

[data-testid="metric-container"]{
    background:white;
    border-radius:12px;
    padding:15px;
    box-shadow:0px 2px 8px rgba(0,0,0,0.08);
}

</style>
""", unsafe_allow_html=True)

with st.sidebar:

    st.image(
        "https://img.icons8.com/color/96/artificial-intelligence.png",
        width=80
    )

    st.title("Project Information")

    st.write("""
This AI application evaluates a student's concept understanding using speech.
""")

    st.divider()

    st.subheader("✨ Features")

    st.markdown("""
- 🎤 Speech to Text
- 🧠 Semantic Analysis
- 🎵 Audio Features
- 📈 Waveform
- 🏆 Final Evaluation
- 📄 PDF Report
""")

    st.divider()

    st.subheader("🛠 Tech Stack")

    st.markdown("""
- Python
- Streamlit
- Whisper AI
- Sentence Transformers
- Librosa
- NumPy
- ReportLab
""")

    st.divider()

    st.success("AI Powered Project")

st.markdown("""
<div class="main-title">
🎤 Voice Based Concept Understanding Analyser
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="sub-title">
AI Powered Student Speech Evaluation System
</div>
""", unsafe_allow_html=True)

st.divider()

st.markdown('<div class="card">', unsafe_allow_html=True)

st.subheader("📖 Reference Answer")

reference_answer = st.text_area(
    "Teacher's Expected Answer",
    height=180,
    placeholder="Enter the teacher's reference answer..."
)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)

st.subheader("👨‍🎓 Student Information")

col1, col2 = st.columns(2)

with col1:
    student_name = st.text_input(
        "Student Name *",
        placeholder="Enter student name"
    )

with col2:
    roll_number = st.text_input(
        "Roll Number *",
        placeholder="Enter roll number"
    )

col3, col4 = st.columns(2)

with col3:
    subject = st.selectbox(
        "Subject",
        [
            "Artificial Intelligence",
            "Operating System",
            "DBMS",
            "Computer Networks",
            "Machine Learning",
            "Java",
            "Python",
            "Other"
        ]
    )

with col4:
    section = st.text_input(
        "Section",
        placeholder="A / B / C"
    )

st.markdown("</div>", unsafe_allow_html=True)

st.subheader("📤 Upload Student Audio")

st.write("Upload a student's MP3 or WAV recording.")

# Upload audio
uploaded_file = st.file_uploader(
    "Choose an audio file",
    type=["mp3", "wav"]
)

# Record audio
st.markdown("### 🎙 Or Record Your Voice")

recorded_audio = mic_recorder(
    start_prompt="🎤 Start Recording",
    stop_prompt="⏹ Stop Recording",
    key="recorder"
)
if recorded_audio and recorded_audio["bytes"] is None:
    st.error("Recording failed. Please record again.")
    st.stop()

# Continue if either upload or recording is available
if uploaded_file is not None or recorded_audio:

    os.makedirs("audio", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # Uploaded file
    if uploaded_file is not None:

        audio_path = os.path.join(
            "audio",
            uploaded_file.name
        )

        with open(audio_path, "wb") as f:
            f.write(uploaded_file.read())

        st.success("✅ Audio uploaded successfully!")

    # Recorded audio
    else:

        audio_path = os.path.join(
            "audio",
            "recorded_audio.wav"
        )

        with open(audio_path, "wb") as f:
            f.write(recorded_audio["bytes"])

        st.success("✅ Voice recorded successfully!")

    st.audio(audio_path)

    col1, col2 = st.columns([3, 1])

    with col1:
        analyze = st.button(
            "🚀 Analyze Audio",
            use_container_width=True
        )

    with col2:
        st.metric(
            "Status",
            "Ready"
        )

    if analyze:

        if not student_name.strip():
            st.error("Please enter Student Name.")
            st.stop()

        if not roll_number.strip():
            st.error("Please enter Roll Number.")
            st.stop()

        if not reference_answer.strip():
            st.error("Please enter the Reference Answer.")
            st.stop()

        with st.spinner("🤖 AI is analyzing the audio..."):

            transcript = transcribe_audio(audio_path)
            if transcript.strip() == "":
                st.error("Speech could not be recognized. Please upload a clearer audio.")
                st.stop()

            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.subheader("📝 Transcript")

            st.write(transcript)

            st.markdown("</div>", unsafe_allow_html=True)

            similarity = calculate_similarity(
                reference_answer,
                transcript
            )

            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.subheader("🧠 Semantic Similarity")

            st.progress(
                min(similarity / 100, 1.0)
            )

            st.metric(
                "Similarity",
                f"{similarity:.2f}%"
            )

            if similarity >= 85:
                st.success("Excellent Concept Match")
            elif similarity >= 70:
                st.warning("Moderate Concept Match")
            else:
                st.error("Low Concept Match")

            st.markdown("</div>", unsafe_allow_html=True)

            features = extract_audio_features(
                audio_path,
                transcript
            )

            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.subheader("🎵 Audio Features")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "⏱ Duration",
                    f"{features['duration']} sec"
                )

            with col2:
                st.metric(
                    "🗣 Speech Rate",
                    f"{features['speech_rate']} WPM"
                )

            with col3:
                st.metric(
                    "🔊 Energy",
                    features["energy"]
                )

            st.markdown("</div>", unsafe_allow_html=True)

            waveform_path = plot_waveform(audio_path)

            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.subheader("📈 Audio Waveform")

            st.image(
                waveform_path,
                use_container_width=True
            )

            st.markdown("</div>", unsafe_allow_html=True)

            final_score, feedback = calculate_score(
                similarity,
                features
            )
            save_result(
            student_name,
            roll_number,
            subject,
            similarity,
            final_score,
            feedback
            )

            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.subheader("🏆 Final Evaluation")

            st.metric(
                "Overall Score",
                f"{final_score:.2f}/100"
            )

            st.progress(
                min(final_score / 100, 1.0)
            )

            if final_score >= 85:
                st.success("🟢 " + feedback)
            elif final_score >= 65:
                st.warning("🟡 " + feedback)
            else:
                st.error("🔴 " + feedback)

            st.markdown("</div>", unsafe_allow_html=True)

            pdf_path = generate_pdf(
                student_name=student_name,
                roll_number=roll_number,
                subject=subject,
                section=section,
                transcript=transcript,
                similarity=similarity,
                features=features,
                final_score=final_score,
                feedback=feedback,
                output_path=f"reports/{roll_number}_Concept_Report.pdf"
            )
            st.success("🎉 Evaluation Completed Successfully!")
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_file,
                    file_name=f"{roll_number}_Concept_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            

st.subheader("📊 Evaluation History")

if os.path.exists("data/results.csv"):
    history = pd.read_csv("data/results.csv")
    st.dataframe(history, use_container_width=True)

if os.path.exists("data/results.csv"):

    dashboard = get_dashboard_data()

    st.subheader("📊 Dashboard Analytics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Evaluations",
            dashboard["total"]
        )

    with col2:
        st.metric(
            "Average Score",
            f"{dashboard['average']}%"
        )

    with col3:
        st.metric(
            "Highest Score",
            f"{dashboard['highest']}%"
        )

    feedback_counts = {
        "Strong": dashboard["strong"],
        "Moderate": dashboard["moderate"],
        "Needs Improvement": dashboard["weak"]
    }

    fig = px.pie(
        names=list(feedback_counts.keys()),
        values=list(feedback_counts.values()),
        title="Feedback Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.histogram(
        dashboard["df"],
        x="Final Score",
        nbins=10,
        title="Final Score Distribution"
    )

    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.line(
        dashboard["df"],
        y="Similarity",
        title="Student Similarity Scores"
    )

    st.plotly_chart(fig3, use_container_width=True)

st.divider()

st.caption(
    "© 2026 Voice Based Concept Understanding Analyser "
)