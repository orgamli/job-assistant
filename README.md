# Job Application Assistant

An AI-powered web app that tailors CVs and generates cover letters 
using the Anthropic Claude API.

## Features
- CV tailoring to match any job description
- Match score analysis with strengths and gaps
- Cover letter generation
- Alternative position suggestions
- Chat refinement with undo
- Export to Word document

## Tech Stack
- Python
- Streamlit
- Anthropic Claude API
- python-docx / pdf2docx

## How to Run Locally

1. Clone the repository:
   git clone https://github.com/yourusername/job-assistant.git
   cd job-assistant

2. Create and activate virtual environment:
   python -m venv venv
   source venv/Scripts/activate

3. Install dependencies:
   pip install -r requirements.txt

4. Add your API key:
   Create a .env file and add:
   ANTHROPIC_API_KEY=your-key-here

5. Run the app:
   streamlit run app.py

## Note
Never share your .env file or API key publicly.