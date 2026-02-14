from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ChatRequest(BaseModel):
    query: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]] = []


class IngestRequest(BaseModel):
    texts: List[str]
    metadatas: Optional[List[Dict[str, Any]]] = None


class IngestResponse(BaseModel):
    status: str
    chunks_added: int


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"


class SessionResponse(BaseModel):
    sessions: List[str]
