<<<<<<< HEAD

import uuid
from typing import Optional


class PDFStore:
    def __init__(self):
        self._store: dict[str, str] = {}
        self._metadata:dict[str,str]={}
        self._metrics={
            "pdfs_uploaded":0,
            "questions_asked":0,
            "summaries_generated":0,
            "quizzes_created":0,
            "flashcards_generated":0
        }

    def save(self, filename: str, text: str) -> str:
        doc_id = str(uuid.uuid4())
        self._store[doc_id] = text
        self._metadata[doc_id]=filename
        self._metrics["pdfs_uploaded"]+=1
        return doc_id

    def get(self, doc_id: str) -> Optional[str]:
        return self._store.get(doc_id)

    def delete(self, doc_id: str) -> bool:
        self._metadata.pop(doc_id,None)
        return self._store.pop(doc_id, None) is not None
    
    def increment_metric(self,metric_name:str):
        if metric_name in self._metrics:
            self._metrics[metric_name]+=1
    def get_metrics(self)->dict:
        return self._metrics


=======
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


>>>>>>> ed0cc9e1db70706d10adc537488cd678102e05d3
pdf_store = PDFStore()