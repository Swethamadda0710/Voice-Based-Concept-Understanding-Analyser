import streamlit as st
import os

from modules.speech_to_text import transcribe_audio
from modules.semantic_analysis import calculate_similarity
from modules.audio_features import (
    extract_audio_features,
    plot_waveform
)
from modules.scoring import calculate_score
from modules.pdf_report import generate_pdf


# ---------------------------------------
# Streamlit Configuration
# ---------------------------------------
st.set_page_config(
    page_title="Voice Based Concept Understanding Analyser",
    page_icon="🎤",
    layout="wide"
)

st.title("🎤 Voice Based Concept Understanding Analyser")

reference_answer = """
Artificial intelligence is transforming education by helping students learn more effectively.
Machine learning enables computers to learn from data without being explicitly programmed.
Natural language processing allows computers to understand and generate human language.
"""

st.write("Upload an audio file to analyze concept understanding.")

# ---------------------------------------
# Upload Audio
# ---------------------------------------
uploaded_file = st.file_uploader(
    "Choose an audio file",
    type=["mp3", "wav"]
)

if uploaded_file is not None:

    os.makedirs("audio", exist_ok=True)

    audio_path = os.path.join(
        "audio",
        uploaded_file.name
    )

    with open(audio_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("✅ Audio uploaded successfully!")

    st.audio(audio_path)

    # ---------------------------------------
    # Analyze Audio
    # ---------------------------------------
    if st.button("Analyze Audio"):

        with st.spinner("Analyzing... Please wait..."):

            # -----------------------------
            # Speech-to-Text
            # -----------------------------
            transcript = transcribe_audio(audio_path)

            st.subheader("📝 Transcript")
            st.write(transcript)

            # -----------------------------
            # Semantic Similarity
            # -----------------------------
            similarity = calculate_similarity(
                reference_answer,
                transcript
            )

            st.subheader("📚 Semantic Similarity")
            st.success(f"{similarity:.2f}%")

            # -----------------------------
            # Audio Features
            # -----------------------------
            features = extract_audio_features(
                audio_path,
                transcript
            )

            st.subheader("🎵 Audio Features")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Duration",
                    f"{features['duration']} sec"
                )

            with col2:
                st.metric(
                    "Speech Rate",
                    f"{features['speech_rate']} WPM"
                )

            with col3:
                st.metric(
                    "Energy",
                    f"{features['energy']}"
                )

            # -----------------------------
            # Waveform
            # -----------------------------
            st.subheader("📈 Audio Waveform")

            waveform_path = plot_waveform(audio_path)

            st.image(
                waveform_path,
                caption="Audio Waveform",
                use_container_width=True
            )

            # -----------------------------
            # Final Score
            # -----------------------------
            final_score, feedback = calculate_score(
                similarity,
                features
            )

            st.subheader("🏆 Final Evaluation")

            st.metric(
                "Final Score",
                f"{final_score:.2f}"
            )

            st.success(feedback)

            # -----------------------------
            # Generate PDF
            # -----------------------------
            os.makedirs(
                "reports",
                exist_ok=True
            )

            pdf_path = generate_pdf(
                transcript,
                similarity,
                features,
                final_score,
                feedback,
                output_path="reports/Concept_Report.pdf"
            )

            st.success("✅ PDF Report Generated Successfully!")

            # -----------------------------
            # Download PDF
            # -----------------------------
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_file,
                    file_name="Concept_Report.pdf",
                    mime="application/pdf"
                )