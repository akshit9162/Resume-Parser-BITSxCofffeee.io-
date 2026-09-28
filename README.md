# Resume Parser (BITS × Coffeee.io)

Turns unstructured resumes (PDF or DOCX) into structured records: name, email, phone, links,
skills, projects and certifications. Built during a software development internship at Coffeee.io
(May–Jul 2025).

## How it works

| Step | Approach | Code |
|---|---|---|
| Text extraction | `pdfminer.six` for PDF, `docx2txt` for DOCX | `extract_text_from_file` |
| Name | spaCy named-entity recognition (`PERSON`) over the first lines, with a heuristic fallback | `extract_name` |
| Email, phone, links | Regular expressions (LinkedIn, GitHub and other URLs) | `extract_email`, `extract_phone`, `extract_links` |
| Section boundaries | Fuzzy matching of lines against section keywords (`partial_ratio > 85`), so "Projects", "Academic Projects" and typos all match | `extract_sections` |
| Skills | Match against a skill vocabulary | `skill_match` |
| Projects, certifications | Group lines under each section into entries | `parse_projects`, `parse_certifications` |

## Output

- **JSON** per resume
- **CSV** export (`export_to_csv`)
- **SQLite** storage (`output/resumes.db`, `export_to_sqlite`)
- **Batch mode**: parse every resume in a folder (`process_resume_folder`)
- **Streamlit UI** (`streamlit_app.py`): upload a resume, view the parsed JSON, download JSON or CSV

## Run

```bash
pip install spacy pdfminer.six docx2txt fuzzywuzzy streamlit
python -m spacy download en_core_web_sm
streamlit run streamlit_app.py
```

## Contributors

- **Akshit Gupta**: the offline parser (`parser.py`): extraction, section detection, batch processing, CSV and SQLite export, and the Streamlit UI.
- **Ashutosh**: education and work-experience extraction (`advanced_fields.py`) and an alternative parser using the Gemini API (`gemini-parse.py`).
