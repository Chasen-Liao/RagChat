from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json

from .models import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    SessionResponse,
)
from .chain import chat, stream_chat, history_manager

app = FastAPI(
    title="RAG Chatbot API",
    description="基于 LangChain 的 RAG 聊天助手",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy")


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        result = chat(request.query, request.session_id)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    async def event_generator():
        try:
            async for chunk in stream_chat(request.query, request.session_id):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/sessions", response_model=SessionResponse)
async def get_sessions():
    return SessionResponse(sessions=history_manager.get_all_sessions())


@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    history_manager.clear_session(session_id)
    return {"status": "cleared"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
