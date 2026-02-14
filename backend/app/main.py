import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json

from .models import (
    ChatRequest,
    ChatResponse,
    IngestRequest,
    IngestResponse,
    HealthResponse,
    SessionResponse,
)
from .chain import chat, stream_chat
from .vectorstore import vectorstore_manager
from .memory import history_manager

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


@app.post("/ingest", response_model=IngestResponse)
async def ingest_text(request: IngestRequest):
    try:
        chunks_added = vectorstore_manager.add_documents(
            request.texts, request.metadatas
        )
        return IngestResponse(status="success", chunks_added=chunks_added)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/file", response_model=IngestResponse)
async def ingest_file(file: UploadFile = File(...)):
    try:
        content = await file.read()

        if file.filename.endswith(".pdf"):
            try:
                import fitz

                pdf_document = fitz.open(stream=content, filetype="pdf")
                text = ""
                for page in pdf_document:
                    text += page.get_text()
            except ImportError:
                raise HTTPException(
                    status_code=500,
                    detail="PDF processing requires PyMuPDF: pip install PyMuPDF",
                )
        else:
            text = content.decode("utf-8")

        chunks_added = vectorstore_manager.add_documents(
            [text], [{"source": file.filename}]
        )

        return IngestResponse(status="success", chunks_added=chunks_added)
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File encoding not supported")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
