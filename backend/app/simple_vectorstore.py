from typing import List, Optional, Dict, Any
import requests
from .config import settings


class SimpleVectorStore:
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: List[List[float]] = []

    def add_texts(self, texts: List[str], metadatas: Optional[List[dict]] = None):
        url = f"{settings.siliconflow_api_base}/embeddings"
        headers = {
            "Authorization": f"Bearer {settings.siliconflow_api_key}",
            "Content-Type": "application/json",
        }

        batch_size = 32
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            payload = {"model": settings.embedding_model, "input": batch}
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                for j, emb_data in enumerate(result.get("data", [])):
                    self.embeddings.append(emb_data.get("embedding", []))
                    meta = (
                        metadatas[i + j] if metadatas and i + j < len(metadatas) else {}
                    )
                    meta["chunk_index"] = i + j
                    self.documents.append({"content": batch[j], "metadata": meta})
            else:
                print(f"Error embedding batch: {response.text}")

        return len(texts)

    def similarity_search(self, query: str, k: int = 4) -> List[Dict]:
        if not self.embeddings:
            return []

        url = f"{settings.siliconflow_api_base}/embeddings"
        headers = {
            "Authorization": f"Bearer {settings.siliconflow_api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": settings.embedding_model, "input": [query]}
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
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


vector_store = SimpleVectorStore()
