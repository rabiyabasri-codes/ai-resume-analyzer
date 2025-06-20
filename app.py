from flask import Flask, render_template, request, jsonify
import json
import os
from collections import defaultdict
import re
from datetime import datetime
import sys
import subprocess
import string

app = Flask(__name__)

def ensure_spacy_model():
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
            return nlp
        except OSError:
            print("Downloading spaCy model...")
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            return spacy.load("en_core_web_sm")
    except ImportError:
        print("Installing spaCy...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "spacy==3.7.2"])
        import spacy
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        return spacy.load("en_core_web_sm")

def ensure_pymupdf():
    try:
        import fitz
        return fitz
    except ImportError:
        print("Installing PyMuPDF...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyMuPDF==1.21.1"])
        import fitz
        return fitz

# Initialize required components
print("Initializing components...")
nlp = ensure_spacy_model()
fitz = ensure_pymupdf()

# Create necessary directories
REQUIRED_DIRS = ['uploads', 'static', 'templates']
for directory in REQUIRED_DIRS:
    if not os.path.exists(directory):
        os.makedirs(directory)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    try:
        text = ""
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF file: {str(e)}")

def calculate_score(found_keywords, total_keywords):
    if total_keywords == 0:
        return 0
    return round((len(found_keywords) / total_keywords) * 100, 2)

def get_recommendations(missing_keywords, category):
    recommendations = {
        "technical_skills": "Consider adding these technical skills to your resume. Focus on the ones most relevant to your target role.",
        "tools": "These tools are commonly used in the industry. Adding experience with these tools can make your resume stand out.",
        "certifications": "These certifications can boost your credibility. Consider pursuing the ones that align with your career goals.",
        "soft_skills": "These soft skills are highly valued. Try to demonstrate these through your work experience and achievements."
    }
    return recommendations.get(category, "Consider adding these to strengthen your profile.")

def normalize(text):
    # Lowercase, remove punctuation, and extra spaces
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = ' '.join(text.split())
    return text

def analyze_resume(text, role_data):
    text = normalize(text)
    results = {
        "found": defaultdict(list),
        "missing": defaultdict(list),
        "scores": {},
        "recommendations": {}
    }
    
    total_keywords = 0
    found_keywords = set()
    
    for category, keywords in role_data.items():
        category_found = []
        category_missing = []
        
        for keyword in keywords:
            total_keywords += 1
            normalized_keyword = normalize(keyword)
            if normalized_keyword in text:
                category_found.append(keyword)
                found_keywords.add(keyword)
            else:
                category_missing.append(keyword)
        
        results["found"][category] = category_found
        results["missing"][category] = category_missing
        results["scores"][category] = calculate_score(category_found, len(keywords))
        results["recommendations"][category] = get_recommendations(category_missing, category)
    
    results["overall_score"] = calculate_score(found_keywords, total_keywords)
    return results

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file uploaded"}), 400
    
    resume = request.files['resume']
    job_role = request.form.get('role')
    
    if not job_role:
        return jsonify({"error": "No job role selected"}), 400
    
    if resume.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not allowed_file(resume.filename):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    file_path = None
    try:
        # Save file with timestamp to prevent overwriting
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{resume.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        resume.save(file_path)

        # Load role keywords
        with open('job_keywords.json') as f:
            job_data = json.load(f)
        
        if job_role not in job_data:
            raise ValueError("Invalid job role selected")

        role_keywords = job_data[job_role]
        resume_text = extract_text_from_pdf(file_path)
        analysis_results = analyze_resume(resume_text, role_keywords)

        # Convert defaultdicts to dicts for Jinja2 compatibility
        analysis_results["found"] = dict(analysis_results["found"])
        analysis_results["missing"] = dict(analysis_results["missing"])

        return render_template('results.html', 
                             role=job_role,
                             results=analysis_results)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        # Clean up the uploaded file
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

if __name__ == "__main__":
    print("Starting Resume Analyzer application...")
    app.run(debug=True)
