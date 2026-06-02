"""
Retrieval-Augmented Generation helper.

Strategy
--------
1. Split the document into overlapping chunks.
2. For each task, pick the most relevant chunks via TF-IDF cosine similarity
   against a task-specific seed query.
3. Return a context string that fits inside the model's token budget.
"""
from __future__ import annotations

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── Config ────────────────────────────────────────────────────────────────────

CHUNK_SIZE = 400        # words per chunk
CHUNK_OVERLAP = 80      # words of overlap between consecutive chunks
MAX_CONTEXT_WORDS = 900 # keep context under flan-t5-large's ~512-token sweet spot

TASK_QUERIES = {
    "summarize":   "main idea key points overview summary",
    "mcq":         "important facts concepts definitions examples",
    "flashcards":  "key terms definitions concepts vocabulary",
}


# ── Public API ────────────────────────────────────────────────────────────────

def build_rag_context(text: str, task: str) -> str:
    chunks = _chunk_text(text)
    if not chunks:
        return text[:MAX_CONTEXT_WORDS * 6]  # fallback: first N chars

    query = TASK_QUERIES.get(task, "important information")
    ranked = _rank_chunks(chunks, query)

    context_words: list[str] = []
    for chunk in ranked:
        words = chunk.split()
        if len(context_words) + len(words) > MAX_CONTEXT_WORDS:
            break
        context_words.extend(words)

    return " ".join(context_words)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _chunk_text(text: str) -> list[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + CHUNK_SIZE
        chunks.append(" ".join(words[start:end]))
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def _rank_chunks(chunks: list[str], query: str) -> list[str]:
    try:
        corpus = [query] + chunks
        vec = TfidfVectorizer(stop_words="english")
        tfidf = vec.fit_transform(corpus)
        scores = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
        ranked_idx = scores.argsort()[::-1]
        return [chunks[i] for i in ranked_idx]
    except Exception:
        return chunks  # fallback: original order