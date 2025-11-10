import io
import re
import uuid
from typing import Any, Dict

import fitz  # PyMuPDF
from docx import Document
from fastapi import FastAPI, Form, Request, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


class InMemoryResumeStore:
    """Simple in-memory storage for uploaded resume analyses."""

    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, Any]] = {}

    def add_record(self, resume_text: str, job_description: str) -> str:
        record_id = str(uuid.uuid4())
        self._store[record_id] = {
            "resume_text": resume_text,
            "job_description": job_description,
        }
        return record_id

    def get_record(self, record_id: str) -> Dict[str, Any]:
        try:
            return self._store[record_id]
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Record not found") from exc


def clean_text(text: str) -> str:
    """Normalize whitespace and strip leading/trailing blank lines."""
    normalized = re.sub(r"\s+", " ", text)
    return normalized.strip()


def extract_text_from_pdf(data: bytes) -> str:
    with fitz.open(stream=data, filetype="pdf") as document:
        text = "\n".join(page.get_text("text") for page in document)
    return text


def extract_text_from_docx(data: bytes) -> str:
    with io.BytesIO(data) as buffer:
        document = Document(buffer)
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    return text


def extract_resume_text(uploaded_file: UploadFile) -> str:
    data = uploaded_file.file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    filename = uploaded_file.filename or ""
    if filename.lower().endswith(".pdf"):
        extracted = extract_text_from_pdf(data)
    elif filename.lower().endswith((".doc", ".docx")):
        extracted = extract_text_from_docx(data)
    else:
        raise HTTPException(
            status_code=415,
            detail="Unsupported file type. Please upload a PDF or DOCX resume.",
        )

    cleaned = clean_text(extracted)
    if not cleaned:
        raise HTTPException(
            status_code=422, detail="No readable text could be extracted from the file."
        )
    return cleaned


app = FastAPI(title="AI-Driven Resume Analyzer")
app.state.resume_store = InMemoryResumeStore()

# Static folder placeholder for future assets (CSS/JS/images)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "analysis": None},
    )


@app.post("/analyze", response_class=HTMLResponse)
async def analyze_resume(
    request: Request,
    resume: UploadFile,
    job_description: str = Form("")
) -> HTMLResponse:
    resume_text = extract_resume_text(resume)
    cleaned_job_description = clean_text(job_description)
    record_id = app.state.resume_store.add_record(resume_text, cleaned_job_description)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "analysis": {
                "id": record_id,
                "resume_text": resume_text,
                "job_description": cleaned_job_description,
            },
        },
    )


@app.get("/analysis/{record_id}", response_class=HTMLResponse)
async def get_analysis(record_id: str, request: Request) -> HTMLResponse:
    record = app.state.resume_store.get_record(record_id)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "analysis": {
                "id": record_id,
                "resume_text": record["resume_text"],
                "job_description": record["job_description"],
            },
        },
    )
