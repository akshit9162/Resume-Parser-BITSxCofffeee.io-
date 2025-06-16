import os
import argparse
import json
import pathlib
import textwrap
import google.generativeai as genai
from dotenv import load_dotenv
from pypdf import PdfReader
from pdfminer.high_level import extract_text

def extract_text_from_file(file_path):
   return extract_text(file_path)

def get_gemini_response(resume_text, api_key):
    genai.configure(api_key=api_key)
    print("here")
    prompt = textwrap.dedent("""
        You are an expert resume parser. Your task is to analyze the provided resume text and extract key information into a structured JSON format.

        The JSON object must have the following top-level keys: "Skills", "Education", "Work Experience", and "Projects".

        Follow this specific schema:
        {
          "Skills": [
            "Skill 1",
            "Skill 2",
            ...
          ],
          "Education": [
            {
              "institution": "University Name",
              "degree": "Degree (e.g., Bachelor of Science in Computer Science)",
              "Grade": null if not found
              "graduation_date": "Month Year (e.g., May 2020)",
              "location": "City, State"
            }
          ],
          "Work Experience": [
            {
              "company": "Company Name",
              "job_title": "Your Title",
              "start_date": "Month Year",
              "end_date": "Month Year or 'Present'",
              "location": "City, State",
              "responsibilities": [
                "A bullet point describing a key achievement or responsibility.",
                "Another bullet point."
              ]
            }
          ],
          "Projects": [
            {
              "name": "Project Name",
              "description": "A brief description of the project.",
              "technologies": [
                "Tech 1",
                "Tech 2"
              ],
              "link": "URL to the project if available"
            }
          ]
        }

        Important Rules:
        1.  The entire output MUST be a single, valid JSON object. Do not include any text, explanations, or markdown formatting like ```json before or after the JSON.
        2.  If a section (like "Projects") is not found in the resume, its value should be an empty array `[]`.
        3.  If a specific field within an object (like a project's "link") is not found, its value should be `null`.
        4.  Analyze the following resume text and generate the JSON:

        --- RESUME TEXT START ---"""+
        resume_text
        +"--- RESUME TEXT END ---"
    )
 
    model = genai.GenerativeModel('gemini-2.0-flash') 
    response = model.generate_content(prompt)
    
    return response.text

def main():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    try:
      filename='./resume11.pdf'
      print(f"Reading resume  {filename}")
      resume_text = extract_text_from_file(filename)

      print("sending text to Gemini API ")
      gemini_output = get_gemini_response(resume_text, api_key)

      
      cleaned_json_string = gemini_output.strip().replace('```json', '').replace('```', '').strip()
      
      print("Parsing JSON response...")
      parsed_json = json.loads(cleaned_json_string)

      with open("output_data.json", 'w', encoding='utf-8') as f:
          json.dump(parsed_json, f, indent=2, ensure_ascii=False)
        
      print(f"Successfully parsed resume ")
    except Exception as e:
        print(f"error: {e}")

if __name__ == "__main__":
    main()