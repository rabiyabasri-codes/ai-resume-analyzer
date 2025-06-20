# AI Resume Analyzer

An intelligent resume analysis tool that helps job seekers improve their resumes by comparing them against industry-standard keywords for specific roles.

## Features

- Upload PDF resumes for analysis
- Compare resume content against role-specific keywords
- Get suggestions for missing keywords and skills
- Modern, user-friendly interface
- Support for multiple job roles

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Select your target job role from the dropdown menu
2. Upload your resume in PDF format
3. Click "Analyze Resume" to get instant feedback
4. Review the found and missing keywords
5. Use the suggestions to improve your resume

## Supported Job Roles

- Data Scientist
- Web Developer
- AI Engineer

## Technologies Used

- Python
- Flask
- spaCy (NLP)
- PyMuPDF (PDF processing)
- Bootstrap 5
- HTML/CSS 