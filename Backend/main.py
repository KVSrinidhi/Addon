from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from services.pdf_parser import extract_text_from_pdf
from services.rag import build_rag_context
from services.llm import (
    generate_summary,
    generate_mcq,
    generate_flashcards,
)
from storage import pdf_store

app = FastAPI(title="PDF Learning API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Upload ────────────────────────────────────────────────────────────────────

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    raw_bytes = await file.read()
    text = extract_text_from_pdf(raw_bytes)

    if not text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from PDF.")

    doc_id = pdf_store.save(file.filename, text)
    return {"doc_id": doc_id, "filename": file.filename, "char_count": len(text)}


# ── Shared request model ──────────────────────────────────────────────────────

class DocRequest(BaseModel):
    doc_id: str


# ── Summarize ─────────────────────────────────────────────────────────────────

@app.post("/summarize")
async def summarize(req: DocRequest):
    text = _get_text(req.doc_id)
    context = build_rag_context(text, task="summarize")
    summary = generate_summary(context)
    return {"summary": summary}


# ── MCQ Quiz ──────────────────────────────────────────────────────────────────

@app.post("/mcq")
async def mcq_quiz(req: DocRequest):
    text = _get_text(req.doc_id)
    context = build_rag_context(text, task="mcq")
    questions = generate_mcq(context)
    return {"questions": questions}


# ── Flash Cards ───────────────────────────────────────────────────────────────

@app.post("/flashcards")
async def flashcards(req: DocRequest):
    text = _get_text(req.doc_id)
    context = build_rag_context(text, task="flashcards")
    cards = generate_flashcards(context)
    return {"flashcards": cards}


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


# ── Helper ────────────────────────────────────────────────────────────────────

def _get_text(doc_id: str) -> str:
    text = pdf_store.get(doc_id)
    if text is None:
        raise HTTPException(status_code=404, detail="Document not found. Please upload again.")
    return text


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)