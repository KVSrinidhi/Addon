# PDF Learning API

FastAPI backend for the PDF learning app — Upload a PDF, then Summarize, generate MCQ Quiz, or create Flash Cards using `google/flan-t5-large` with a TF-IDF RAG pipeline.

---

## Project Structure

```
.
├── main.py              # FastAPI app & routes
├── storage.py           # In-memory PDF store
├── requirements.txt
└── services/
    ├── pdf_parser.py    # PDF → text  (PyMuPDF)
    ├── rag.py           # Chunking + TF-IDF retrieval
    └── llm.py           # flan-t5-large inference
```

---

## Setup

```bash
pip install -r requirements.txt
python main.py          # runs on http://localhost:8000
```

Interactive docs → http://localhost:8000/docs

---

## API Reference

### POST /upload
Upload a PDF file.

**Form data:** `file` (PDF)

**Response:**
```json
{ "doc_id": "uuid", "filename": "notes.pdf", "char_count": 12400 }
```

---

### POST /summarize
**Body:**
```json
{ "doc_id": "uuid" }
```
**Response:**
```json
{ "summary": "The document covers..." }
```

---

### POST /mcq
**Body:**
```json
{ "doc_id": "uuid" }
```
**Response:**
```json
{
  "questions": [
    {
      "question": "What is ...?",
      "options": { "A": "...", "B": "...", "C": "...", "D": "..." },
      "answer": "B"
    }
  ]
}
```

---

### POST /flashcards
**Body:**
```json
{ "doc_id": "uuid" }
```
**Response:**
```json
{
  "flashcards": [
    { "front": "RAG", "back": "Retrieval-Augmented Generation — combining retrieval with generation" }
  ]
}
```

---

### GET /health
```json
{ "status": "ok" }
```

---

## Notes

- PDFs are stored **in-memory only** — they are lost when the server restarts.
- The flan-t5-large model (~800 MB) is downloaded from Hugging Face on first run and cached locally.
- To switch models, change `MODEL_ID` in `services/llm.py`.
- For production, add authentication and replace in-memory storage with a database.
