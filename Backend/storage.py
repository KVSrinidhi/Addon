"""
In-memory store for uploaded PDF text.
Maps  doc_id (uuid)  →  extracted text string.
"""
import uuid
from typing import Optional


class PDFStore:
    def __init__(self):
        self._store: dict[str, str] = {}

    def save(self, filename: str, text: str) -> str:
        doc_id = str(uuid.uuid4())
        self._store[doc_id] = text
        return doc_id

    def get(self, doc_id: str) -> Optional[str]:
        return self._store.get(doc_id)

    def delete(self, doc_id: str) -> bool:
        return self._store.pop(doc_id, None) is not None


pdf_store = PDFStore()