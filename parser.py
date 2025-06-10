import re
import json
import os
import docx2txt
from pdfminer.high_level import extract_text
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_text_from_file(file_path):
    if file_path.endswith('.pdf'):
        return extract_text(file_path)
    elif file_path.endswith('.docx'):
        return docx2txt.process(file_path)
    else:
        raise ValueError("Unsupported file format: Only PDF and DOCX are supported.")

def extract_email(text):
    match = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match[0] if match else None

def extract_phone(text):
    match = re.findall(r"(\+?\d[\d\s\-\(\)]{9,}\d)", text)
    return match[0] if match else None

def extract_links(text):
    return re.findall(r'(https?://[^\s]+)', text)

def extract_name(text):
    lines = text.split('\n')[:10]
    for line in lines:
        doc = nlp(line.strip())
        for ent in doc.ents:
            if ent.label_ == "PERSON" and len(ent.text.split()) <= 3:
                return ent.text
    for line in lines:
        if line.strip() and line.strip()[0].isupper():
            return line.strip()
    return None

SKILL_SET = {
    "python", "java", "c++", "c#", "sql", "excel", "javascript", "html", "css",
    "machine learning", "deep learning", "nlp", "data analysis", "data science",
    "pandas", "numpy", "tensorflow", "keras", "react", "node.js", "django", "flask",
    "git", "linux", "aws", "azure", "docker", "kubernetes", "power bi", "tableau"
}

def extract_skills(text):
    text = text.lower()
    extracted = set()
    for skill in SKILL_SET:
        if skill in text:
            extracted.add(skill)
    return list(extracted)

def parse_resume(file_path):
    text = extract_text_from_file(file_path)
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "links": extract_links(text),
        "skills": ', '.join(extract_skills(text)),
        "raw_text_preview": text[:500] + "..."
    }

if __name__ == "__main__":
    input_file = "data/sample_resume.pdf" 
    result = parse_resume(input_file)

    os.makedirs("output", exist_ok=True)

    output_path = "output/parsed_resume.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    print("Parsed data saved to JSON")
