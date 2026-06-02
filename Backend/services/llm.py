"""
LLM service — google/flan-t5-large via Hugging Face transformers.

All three tasks (summarize, MCQ, flashcards) are handled here with
task-specific prompt templates suited to flan-t5's instruction format.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache

from transformers import pipeline, Pipeline

MODEL_ID = "google/flan-t5-large"
MAX_NEW_TOKENS = 512


# ── Model singleton (loaded once on first use) ────────────────────────────────

@lru_cache(maxsize=1)
def _get_pipeline() -> Pipeline:
    return pipeline(
        "text2text-generation",
        model=MODEL_ID,
        max_new_tokens=MAX_NEW_TOKENS,
    )


def _run(prompt: str) -> str:
    pipe = _get_pipeline()
    result = pipe(prompt, do_sample=False)[0]["generated_text"]
    return result.strip()


# ── Summarize ─────────────────────────────────────────────────────────────────

def generate_summary(context: str) -> str:
    prompt = (
        "Summarize the following text in clear, concise paragraphs. "
        "Cover the main ideas and key points.\n\n"
        f"Text:\n{context}\n\nSummary:"
    )
    return _run(prompt)


# ── MCQ Quiz ──────────────────────────────────────────────────────────────────

def generate_mcq(context: str) -> list[dict]:
    prompt = (
        "Generate 5 multiple-choice questions based on the text below. "
        "For each question provide: the question, four options labeled A B C D, "
        "and the correct answer letter. "
        "Format each question exactly like this example:\n"
        "Q: <question>\nA) <option>\nB) <option>\nC) <option>\nD) <option>\nAnswer: <letter>\n\n"
        f"Text:\n{context}\n\nQuestions:"
    )
    raw = _run(prompt)
    return _parse_mcq(raw)


def _parse_mcq(raw: str) -> list[dict]:
    questions = []
    blocks = re.split(r"\n(?=Q:)", raw.strip())
    for block in blocks:
        lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
        q_text = next((l[2:].strip() for l in lines if l.startswith("Q:")), None)
        options = {}
        answer = None
        for line in lines:
            m = re.match(r"^([A-D])\)\s*(.+)", line)
            if m:
                options[m.group(1)] = m.group(2)
            ans = re.match(r"^Answer:\s*([A-D])", line)
            if ans:
                answer = ans.group(1)
        if q_text and len(options) == 4:
            questions.append({"question": q_text, "options": options, "answer": answer})
    return questions


# ── Flash Cards ───────────────────────────────────────────────────────────────

def generate_flashcards(context: str) -> list[dict]:
    prompt = (
        "Create 8 flashcards from the text below. "
        "Each flashcard has a front (a term or question) and a back (definition or answer). "
        "Format each card exactly like:\n"
        "Front: <term or question>\nBack: <definition or answer>\n\n"
        f"Text:\n{context}\n\nFlashcards:"
    )
    raw = _run(prompt)
    return _parse_flashcards(raw)


def _parse_flashcards(raw: str) -> list[dict]:
    cards = []
    blocks = re.split(r"\n(?=Front:)", raw.strip())
    for block in blocks:
        lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
        front = next((l[6:].strip() for l in lines if l.startswith("Front:")), None)
        back  = next((l[5:].strip() for l in lines if l.startswith("Back:")),  None)
        if front and back:
            cards.append({"front": front, "back": back})
    return cards