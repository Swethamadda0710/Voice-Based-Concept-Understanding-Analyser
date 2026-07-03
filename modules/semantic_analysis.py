import streamlit as st
from sentence_transformers import SentenceTransformer, util


@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


def calculate_similarity(reference_answer, transcript):
    model = load_model()

    embedding1 = model.encode(reference_answer, convert_to_tensor=True)
    embedding2 = model.encode(transcript, convert_to_tensor=True)

    similarity = util.cos_sim(embedding1, embedding2)

    return float(similarity[0][0]) * 100