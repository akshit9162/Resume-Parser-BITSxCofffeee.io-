import streamlit as st
import os
import json
import tempfile
from parser import parse_resume_offline, export_to_csv

st.set_page_config(page_title="Resume Parser", layout="centered")
st.title("📄 Resume Parser Web UI")

uploaded_file = st.file_uploader("Upload a resume (PDF or DOCX)", type=["pdf", "docx"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name
    
    st.info(f"Processing: {uploaded_file.name}")
    parsed = parse_resume_offline(tmp_path)
    os.unlink(tmp_path)

    st.subheader("Parsed Resume Data")
    st.json(parsed)

    # Download JSON
    json_str = json.dumps(parsed, indent=2)
    st.download_button("Download as JSON", json_str, file_name="parsed_resume.json", mime="application/json")

    # Download CSV
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as csv_file:
        export_to_csv(parsed, csv_file.name)
        csv_file.seek(0)
        csv_data = csv_file.read()
    st.download_button("Download as CSV", csv_data, file_name="parsed_resume.csv", mime="text/csv") 