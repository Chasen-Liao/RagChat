import os
from typing import List, Optional, Dict, Any
import requests
from .config import settings


class RAGManager:
    _instance = None
    _enabled = False
    _vector_store = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def enabled(self) -> bool:
        return self._enabled

    def enable(self):
        if not self._enabled:
            self._vector_store = SimpleVectorStore()
            self._enabled = True

    def disable(self):
        self._enabled = False
        self._vector_store = None

    @property
    def vector_store(self):
        return self._vector_store

    def add_documents(
        self, texts: List[str], metadatas: Optional[List[dict]] = None
    ) -> int:
        if not self._enabled or not self._vector_store:
            return 0
        return self._vector_store.add_texts(texts, metadatas)

    def similarity_search(self, query: str, k: int = 4) -> List[Dict]:
        if not self._enabled or not self._vector_store:
            return []
        return self._vector_store.similarity_search(query, k=k)


class SimpleVectorStore:
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: List[List[float]] = []

    def add_texts(
        self, texts: List[str], metadatas: Optional[List[dict]] = None
    ) -> int:
        url = f"{settings.siliconflow_api_base}/embeddings"
        headers = {
            "Authorization": f"Bearer {settings.siliconflow_api_key}",
            "Content-Type": "application/json",
        }

        batch_size = 32
        total_added = 0
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            payload = {"model": settings.embedding_model, "input": batch}
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    for j, emb_data in enumerate(result.get("data", [])):
                        self.embeddings.append(emb_data.get("embedding", []))
                        meta = (
                            metadatas[i + j]
                            if metadatas and i + j < len(metadatas)
                            else {}
                        )
                        meta["chunk_index"] = i + j
                        self.documents.append({"content": batch[j], "metadata": meta})
                        total_added += 1
                else:
                    print(f"Error embedding batch: {response.text}")
            except Exception as e:
                print(f"Exception embedding: {e}")

        return total_added

    def similarity_search(self, query: str, k: int = 4) -> List[Dict]:
        if not self.embeddings:
            return []

        url = f"{settings.siliconflow_api_base}/embeddings"
        headers = {
            "Authorization": f"Bearer {settings.siliconflow_api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": settings.embedding_model, "input": [query]}
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code != 200:
                return []
        except:
            return []

        query_embedding = response.json()["data"][0]["embedding"]

        scores = []
        for i, emb in enumerate(self.embeddings):
            score = sum(a * b for a, b in zip(query_embedding, emb))
            scores.append((i, score))

        scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for i, score in scores[:k]:
            if i < len(self.documents):
                results.append(
                    {
                        "page_content": self.documents[i]["content"],
                        "metadata": self.documents[i]["metadata"],
                        "score": score,
                    }
                )

        return results

    def clear(self):
        self.documents = []
        self.embeddings = []


rag_manager = RAGManager()
