# AI-Driven Resume Analyzer

This project is an AI-assisted resume analyzer and job matching platform built with FastAPI. The current milestone supports uploading resumes in PDF or DOCX format, extracting the text, and displaying it alongside an optional job description.

## Getting Started

### Prerequisites

- Python 3.11+
- A virtual environment (recommended)

### Installation

```bash
pip install -r requirements.txt
```

### Running the app

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 in your browser to access the upload form.

## Current Features

- FastAPI backend with HTML form rendered via Jinja2 templates
- Resume upload endpoint accepting PDF and DOCX files
- Text extraction using PyMuPDF (PDF) and python-docx (DOCX)
- Basic text normalization and in-memory storage of recent analyses
- Bootstrap-based interface to review extracted resume text

## Roadmap

- Integrate LLM-powered comparison between resumes and job descriptions
- Highlight missing keywords and provide skill improvement suggestions
- Persist analyses to a lightweight database and enable PDF export
- Polish UI with richer visualizations and loading indicators
