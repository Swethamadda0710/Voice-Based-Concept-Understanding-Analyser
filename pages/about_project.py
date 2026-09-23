import streamlit as st


def render_about_project():
    st.markdown("<div class='eyebrow'>ABOUT THE PROJECT</div><h1>Voice Based Concept<br><em>Understanding Analyser</em></h1><p class='muted'>ConceptLens AI uses speech and semantic intelligence to turn a student's spoken response into a meaningful understanding signal.</p>", unsafe_allow_html=True)
    st.markdown("<div class='hero-banner compact'><div><span class='eyebrow'>PROJECT OBJECTIVE</span><h2>Make assessment more human,<br><em>with a little help from AI.</em></h2><p>Support educators with a faster, evidence-led view of what students understand, how clearly they communicate it, and where the next teaching moment is.</p></div><div class='hero-icon'>🎙️</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-heading'><div><div class='eyebrow'>WORKFLOW</div><h2>From voice to insight</h2></div></div>", unsafe_allow_html=True)
    steps = [("01", "Capture", "Upload or record a natural student response."), ("02", "Transcribe", "Whisper converts speech into searchable text."), ("03", "Understand", "Sentence-BERT and cosine similarity compare meaning with the reference answer."), ("04", "Evaluate", "Audio signals and semantic fit create a clear PDF report.")]
    cols = st.columns(4)
    for column, (number, title, copy) in zip(cols, steps):
        with column:
            st.markdown(f"<div class='step-card'><span>{number}</span><h3>{title}</h3><p>{copy}</p></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-heading'><div><div class='eyebrow'>TECHNOLOGIES USED</div><h2>Built on focused tools</h2></div></div>", unsafe_allow_html=True)
    cols = st.columns(5)
    for column, icon, title, copy in zip(cols, ["◉", "✦", "▣", "▤", "◈"], ["Whisper", "Sentence-BERT", "Streamlit", "SQLite", "ReportLab"], ["Speech to text", "Semantic embeddings", "Interactive UI", "Secure local auth", "PDF generation"]):
        with column:
            st.markdown(f"<div class='tech-card'><div>{icon}</div><b>{title}</b><small>{copy}</small></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-heading'><div><div class='eyebrow'>APPLICATIONS</div><h2>Where ConceptLens AI helps</h2></div></div>", unsafe_allow_html=True)
    application_columns = st.columns(3)
    for column, icon, title, copy in zip(application_columns, ["⌁", "▤", "✦"], ["Classroom assessment", "Concept revision", "Learning feedback"], ["Review spoken answers at scale with consistent signals.", "Identify concepts that need another explanation.", "Give students clear, evidence-based feedback."]):
        with column:
            st.markdown(f"<div class='quick-card'><div class='quick-icon'>{icon}</div><h3>{title}</h3><p>{copy}</p></div>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card future-card'><div class='card-label'>FUTURE ENHANCEMENTS</div><h2>Where we are going next</h2><p>Planned directions include multilingual transcription, richer teacher analytics, LMS integrations, real-time coaching, and expanded accessibility support.</p></div>", unsafe_allow_html=True)