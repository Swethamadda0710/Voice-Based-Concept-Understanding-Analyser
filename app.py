import streamlit as st

st.set_page_config(
    page_title="Voice Based Concept Understanding Analyser",
    page_icon="🎤",
    layout="wide"
)

st.title("🎤 Voice Based Concept Understanding Analyser")

st.markdown("""
Welcome to the AI-powered Voice Based Concept Understanding Analyser.

### Features
- 🎙️ Upload voice recordings
- 📝 Speech-to-Text using Whisper
- 🧠 Semantic Similarity using Sentence-BERT
- 📊 Speech Fluency Analysis
- 📄 PDF Report Generation
""")

uploaded_audio = st.file_uploader(
    "Upload an audio file",
    type=["wav", "mp3", "m4a"]
)

if uploaded_audio:
    st.success("Audio uploaded successfully!")
    st.audio(uploaded_audio)