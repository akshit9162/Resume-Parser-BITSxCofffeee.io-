import re
import spacy
nlp = spacy.load("en_core_web_md")
def extract_education_details(text):
   
    edu_pattern = r'(?:education|academic background|qualifications|academic profile)[\s\S]*?(?=(?:experience|work history|employment|professional experience|projects|project experience|personal projects|$))'
    edu_match = re.search(edu_pattern, text, re.IGNORECASE)
    
    if not edu_match:
        return []
    
    education_section = edu_match.group(0)
    
    edu_entries = re.split(r'(?:\n\s*\n|\n(?=[A-Z][a-z]+\s+(?:University|College|Institute|School)))', education_section)
    edu_entries = [entry.strip() for entry in edu_entries if entry.strip()]
    
    education_details = []
    degree_regex = r'(B\.?Sc|M\.?Sc|B\.?Tech|M\.?Tech|Ph\.?D|Bachelor|Master|Doctor|Diploma|Associate|MBA|BBA|B\.?E|M\.?E)'
    year_regex = r'(19|20)\d{2}'
    gpa_regex = r'(?:GPA|CGPA|Grade Point Average)[\s:]*([0-9.]+)'
    
    for entry in edu_entries:
        degree = re.search(degree_regex, entry, re.IGNORECASE)
        year = re.search(year_regex, entry)
        gpa = re.search(gpa_regex, entry, re.IGNORECASE)
        
        doc = nlp(entry)
        institution = None
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                institution = ent.text
                break
        
        education_details.append({
            'degree': degree.group(0) if degree else None,
            'institution': institution,
            'year': year.group(0) if year else None,
            'gpa': gpa.group(1) if gpa else None,
            'raw': entry
        })
    
    return [e for e in education_details if e['degree'] ]

def extract_work_experience(text):
    
    exp_pattern = r'(?:experience|work history|employment|professional experience)[\s\S]*?(?=(?:education|academic background|qualifications|academic profile|projects|project experience|personal projects|$))'
    exp_match = re.search(exp_pattern, text, re.IGNORECASE)
    
    if not exp_match:
        return []
    
    experience_section = exp_match.group(0)
    
    
    exp_entries = re.split(r'(?:\n\s*\n|\n(?=(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (?:19|20)\d{2}))', experience_section)
    exp_entries = [entry.strip() for entry in exp_entries if entry.strip()]
    
    work_experiences = []
    date_regex = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (?:19|20)\d{2}'
    location_regex = r'(?:Remote|Hybrid|On-site)?\s*(?:Work)?\s*([A-Za-z\s,]+)'
    
    for exp in exp_entries:
       
        dates = re.findall(date_regex, exp, re.IGNORECASE)
        start_date = dates[0] if dates else None
        end_date = dates[1] if len(dates) > 1 else "Present"
        
       
        doc = nlp(exp)
        company = None
        title = None
        location = None
        
       
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                company = ent.text
                break
        
        
        location_match = re.search(location_regex, exp, re.IGNORECASE)
        if location_match:
            location = location_match.group(1).strip()
        
       
        title_patterns = [
            r'(?:Senior|Lead|Principal)?\s*(?:Software|Data|ML|AI|DevOps|Full Stack|Frontend|Backend)?\s*(?:Engineer|Developer|Scientist|Architect|Analyst)',
            r'(?:Project|Technical|Product|Program|Engineering)?\s*(?:Manager|Lead|Head)',
            r'(?:Business|Data|Product|Program|Project)?\s*(?:Analyst|Consultant|Specialist)',
            r'(?:Research|Teaching)?\s*(?:Assistant|Associate|Fellow)',
            r'(?:Intern|Trainee|Apprentice)'
        ]
        
        for pattern in title_patterns:
            title_match = re.search(pattern, exp, re.IGNORECASE)
            if title_match:
                title = title_match.group(0)
                break
        
       
        responsibilities = re.findall(r'[•\-\*]\s*([^\n]+)', exp)
        
        if company and title:
            work_experiences.append({
                'company': company,
                'title': title,
                'location': location,
                'start_date': start_date,
                'end_date': end_date,
                'responsibilities': responsibilities,
                'description': exp
            })
    
    return work_experiences