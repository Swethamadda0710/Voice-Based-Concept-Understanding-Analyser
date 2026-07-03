import streamlit as st
import whisper


@st.cache_resource
def load_model():
    return whisper.load_model("base")


def transcribe_audio(audio_path):
    model = load_model()

    result = model.transcribe(audio_path)

    return result["text"]