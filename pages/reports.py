import os
import pandas as pd
import streamlit as st


def render_reports():
    st.markdown("<div class='eyebrow'>KNOWLEDGE ARCHIVE</div><h1>Reports that tell the <em>whole story.</em></h1><p class='muted'>Search, inspect, and download every evaluation from your workspace.</p>", unsafe_allow_html=True)
    if not os.path.exists("data/results.csv"):
        st.info("Your first analysis will appear here.")
        return
    reports = pd.read_csv("data/results.csv")
    query = st.text_input("Search reports", placeholder="Search by student name, roll number, or subject...", label_visibility="collapsed")
    if query:
        mask = reports.astype(str).apply(lambda column: column.str.contains(query, case=False, na=False)).any(axis=1)
        reports = reports[mask]
    st.markdown(f"<div class='section-heading'><h2>{len(reports)} evaluations</h2><span class='muted'>Sorted by latest</span></div>", unsafe_allow_html=True)
    for index, row in reports.iloc[::-1].iterrows():
        with st.container():
            st.markdown(f"<div class='report-row'><div class='report-avatar'>{str(row['Student Name'])[:1].upper()}</div><div class='report-main'><b>{row['Student Name']}</b><span>{row['Subject']} · Roll {row['Roll Number']}</span></div><div class='report-score'><strong>{float(row['Final Score']):.1f}</strong><small>FINAL SCORE</small></div><div class='report-feedback'>{row['Feedback']}</div></div>", unsafe_allow_html=True)
            if st.button(f"View evaluation · {index}", key=f"view_report_{index}"):
                st.session_state.report_detail = row.to_dict()
    if st.session_state.get("report_detail"):
        detail = st.session_state.report_detail
        st.markdown(f"<div class='glass-card'><div class='card-label'>SELECTED EVALUATION</div><h2>{detail['Student Name']} · {detail['Subject']}</h2><p class='muted'>Similarity {float(detail['Similarity']):.1f}% · Final score {float(detail['Final Score']):.1f}/100</p><p>{detail['Feedback']}</p></div>", unsafe_allow_html=True)