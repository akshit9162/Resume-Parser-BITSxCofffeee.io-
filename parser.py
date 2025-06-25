import re
import os
import json
import csv
import sqlite3
import docx2txt
from pdfminer.high_level import extract_text
import spacy
from fuzzywuzzy import fuzz

nlp = spacy.load("en_core_web_sm")

def extract_text_from_file(file_path):
    if file_path.endswith('.pdf'):
        return extract_text(file_path)
    elif file_path.endswith('.docx'):
        return docx2txt.process(file_path)
    else:
        raise ValueError("Unsupported file format: Only PDF and DOCX are supported.")

def extract_name_spacy(text):
    lines = text.split('\n')[:10]
    for line in lines:
        doc = nlp(line.strip())
        for ent in doc.ents:
            if ent.label_ == "PERSON" and len(ent.text.split()) <= 3:
                return ent.text
    return None

def fallback_extract_name(text):
    lines = text.split('\n')[:10]
    for line in lines:
        if re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+$', line.strip()):
            return line.strip()
    return None

def extract_name(text):
    return extract_name_spacy(text) or fallback_extract_name(text)

def extract_email(text):
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}", text)
    return match.group() if match else None

def extract_phone(text):
    match = re.search(r"(\+?\d[\d\s\-\(\)]{9,}\d)", text)
    return re.sub(r"[^\d+]", "", match.group()) if match else None

def extract_links(text):
    return re.findall(r'(https?://[^\s]+)', text)

SKILL_SET = {
    "python", "java", "c++", "c#", "sql", "excel", "javascript", "html", "css",
    "machine learning", "deep learning", "nlp", "data analysis", "data science",
    "pandas", "numpy", "tensorflow", "keras", "react", "node.js", "django", "flask",
    "git", "linux", "aws", "azure", "docker", "kubernetes", "power bi", "tableau"
}

def fuzzy_skill_match(text, threshold=80):
    found = set()
    text_lower = text.lower()
    for skill in SKILL_SET:
        if fuzz.partial_ratio(skill, text_lower) >= threshold:
            found.add(skill)
    return list(found)

SECTION_HEADERS = {
    "education": ["education", "academic background"],
    "experience": ["experience", "work experience", "professional experience"],
    "certifications": ["certifications", "licenses", "certificates"],
    "projects": ["projects", "personal projects"]
}

def extract_sections(text):
    sections = {key: [] for key in SECTION_HEADERS}
    current = None
    for line in text.split('\n'):
        line_lower = line.strip().lower()
        for section, keywords in SECTION_HEADERS.items():
            if any(fuzz.partial_ratio(line_lower, kw) > 85 for kw in keywords):
                current = section
                break
        else:
            if current and line.strip():
                sections[current].append(line.strip())
    return sections

def group_entries(lines):
    content = '\n'.join(lines)
    entries = re.split(r'\n{2,}', content)
    return [e.strip() for e in entries if e.strip()]

def parse_resume_offline(file_path):
    text = extract_text_from_file(file_path)
    sections = extract_sections(text)

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "links": extract_links(text),
        "skills": ", ".join(fuzzy_skill_match(text)),
        "education": group_entries(sections.get("education", [])),
        "experience": group_entries(sections.get("experience", [])),
        "certifications": group_entries(sections.get("certifications", [])),
        "projects": group_entries(sections.get("projects", [])),
        "raw_preview": text[:400] + "..."
    }

def export_to_csv(data, csv_path):
    headers = ["name", "email", "phone", "links", "skills", "education", "experience", "certifications", "projects"]
    row = {
        "name": data.get("name", ""),
        "email": data.get("email", ""),
        "phone": data.get("phone", ""),
        "links": ", ".join(data.get("links", [])),
        "skills": data.get("skills", ""),
        "education": "\n\n".join(data.get("education", [])),
        "experience": "\n\n".join(data.get("experience", [])),
        "certifications": "\n\n".join(data.get("certifications", [])),
        "projects": "\n\n".join(data.get("projects", []))
    }
    with open(csv_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerow(row)

def export_to_sqlite(data, db_path="output/resumes.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            links TEXT,
            skills TEXT,
            education TEXT,
            experience TEXT,
            certifications TEXT,
            projects TEXT
        )
    ''')
    cursor.execute('''
        INSERT INTO resumes (
            name, email, phone, links, skills,
            education, experience, certifications, projects
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get("name", ""),
        data.get("email", ""),
        data.get("phone", ""),
        ", ".join(data.get("links", [])),
        data.get("skills", ""),
        "\n\n".join(data.get("education", [])),
        "\n\n".join(data.get("experience", [])),
        "\n\n".join(data.get("certifications", [])),
        "\n\n".join(data.get("projects", []))
    ))
    conn.commit()
    conn.close()

def process_resume_folder(folder_path):
    os.makedirs("output", exist_ok=True)
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".pdf") or file_name.endswith(".docx"):
            file_path = os.path.join(folder_path, file_name)
            print(f"\n📄 Processing: {file_name}")
            parsed = parse_resume_offline(file_path)

            json_name = file_name.rsplit('.', 1)[0] + ".json"
            csv_name = file_name.rsplit('.', 1)[0] + ".csv"

            with open(f"output/{json_name}", "w") as f:
                json.dump(parsed, f, indent=2)

            export_to_csv(parsed, f"output/{csv_name}")
            export_to_sqlite(parsed, "output/resumes.db")

if __name__ == "__main__":
    process_resume_folder("data")
    print("\n✅ All resumes processed and saved to output folder (JSON + CSV + SQLite).")