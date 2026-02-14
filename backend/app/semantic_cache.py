import hashlib
import time
from typing import Dict, Optional, List
import numpy as np
from .config import settings
import requests


class SemanticCache:
    """语义缓存：缓存相似查询的结果"""

    def __init__(self, max_size: int = 100, similarity_threshold: float = 0.92):
        self.cache: Dict[
            str, dict
        ] = {}  # query_hash -> {embedding, answer, timestamp, query}
        self.max_size = max_size
        self.threshold = similarity_threshold
        self._embedding_url = f"{settings.siliconflow_api_base}/embeddings"
        self._headers = {
            "Authorization": f"Bearer {settings.siliconflow_api_key}",
            "Content-Type": "application/json",
        }

    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """获取文本的 embedding"""
        try:
            payload = {"model": settings.embedding_model, "input": [text]}
            response = requests.post(
                self._embedding_url, headers=self._headers, json=payload, timeout=10
            )
            if response.status_code == 200:
                return response.json()["data"][0]["embedding"]
        except Exception as e:
            print(f"Cache embedding error: {e}")
        return None

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    def get(self, query: str) -> Optional[str]:
        """从缓存获取答案"""
        query_emb = self._get_embedding(query)
        if not query_emb:
            return None

        best_match = None
        best_score = 0

        for key, item in self.cache.items():
            score = self._cosine_similarity(query_emb, item["embedding"])
            if score > self.threshold and score > best_score:
                best_score = score
                best_match = item

        if best_match:
            print(f"Cache hit! Similarity: {best_score:.3f}")
            best_match["timestamp"] = time.time()  # 更新访问时间
            return best_match["answer"]

        return None

    def set(self, query: str, answer: str):
        """存入缓存"""
        if len(self.cache) >= self.max_size:
            # LRU 淘汰：移除最久未访问的
            oldest = min(self.cache.items(), key=lambda x: x[1]["timestamp"])
            del self.cache[oldest[0]]

        query_emb = self._get_embedding(query)
        if query_emb:
            key = hashlib.md5(query.encode()).hexdigest()
            self.cache[key] = {
                "embedding": query_emb,
                "answer": answer,
                "timestamp": time.time(),
                "query": query,
            }
            print(f"Cached query: {query[:30]}...")

    def clear(self):
        """清空缓存"""
        self.cache.clear()


# 全局缓存实例
semantic_cache = SemanticCache()
