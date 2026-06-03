from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from services.pdf_parser import extract_text_from_pdf
from services.rag import build_rag_context
from services.llm import (
    generate_summary,
    generate_mcq,
    generate_flashcards,
    generate_chat_reply
)
from storage import pdf_store

app = FastAPI(title="PDF Learning API", version="1.0.0")

origins = [
    "http://localhost:5173",  # For local development
    "https://your-frontend-domain.up.railway.app"  # Your Railway frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Or use ["*"] to allow all domains temporarily during testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    doc_id:str
    message:str

class DocRequest(BaseModel):
    doc_id: str

class QuizRequest(BaseModel):
    doc_id: str
    difficulty: str = "medium"
    count: int = Field(default=10, alias="count")


@app.post("/chat")
async def chat_with_doc(req:ChatRequest):
    text=_get_text(req.doc_id)
    context=build_rag_context(text,task="summarize")
    reply = generate_chat_reply(context, req.message)
    pdf_store.increment_metric("questions_asked")
    return {"reply": reply}



# ── Upload ────────────────────────────────────────────────────────────────────

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    raw_bytes = await file.read()
    text = extract_text_from_pdf(raw_bytes)

    # If text is empty, the PDF is either scanned or completely empty
    if not text.strip():
        raise HTTPException(
            status_code=422, 
            detail="Could not extract text from PDF. Scanned documents or image-only PDFs are not supported."
        )

    doc_id = pdf_store.save(file.filename, text)
    return {"doc_id": doc_id, "filename": file.filename, "char_count": len(text)}


# ── Summarize ─────────────────────────────────────────────────────────────────

@app.post("/summarize")
async def summarize(req: DocRequest):
    text = _get_text(req.doc_id)
    context = build_rag_context(text, task="summarize")
    summary = generate_summary(context)
    pdf_store.increment_metric("summaries_generated")
    return {"summary": summary}



@app.post("/mcq")
async def mcq_quiz(req: QuizRequest):
    text = _get_text(req.doc_id)
    context = build_rag_context(text, task=f"mcq_{req.difficulty}")
    
    questions = generate_mcq(context, n=req.count, difficulty=req.difficulty)
    
    pdf_store.increment_metric("quizzes_created")
    return {"questions": questions}

# ── Flash Cards ───────────────────────────────────────────────────────────────

@app.post("/flashcards")
async def flashcards_tool(req: DocRequest):
    text = _get_text(req.doc_id)
    context = build_rag_context(text, task="flashcards")
    
    cards = generate_flashcards(context)
    
    pdf_store.increment_metric("flashcards_generated")
    
    return {"cards": cards}


@app.get("/analytics/metrics")
async def get_dashboard_metrics():
    return pdf_store.get_metrics()

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
