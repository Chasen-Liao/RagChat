import uuid
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
    SessionListResponse,
    SessionData,
    RAGStatusResponse,
    CreateSessionRequest,
)
from .chain import chat, stream_chat
from .rag_manager import rag_manager
from .session_manager import session_manager

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


@app.get("/rag/status", response_model=RAGStatusResponse)
async def rag_status():
    return RAGStatusResponse(enabled=rag_manager.enabled)


@app.post("/rag/enable")
async def rag_enable():
    rag_manager.enable()
    return {"status": "enabled", "enabled": True}


@app.post("/rag/disable")
async def rag_disable():
    rag_manager.disable()
    return {"status": "disabled", "enabled": False}


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
    if not rag_manager.enabled:
        raise HTTPException(status_code=400, detail="RAG is not enabled")
    try:
        chunks_added = rag_manager.add_documents(request.texts, request.metadatas)
        return IngestResponse(status="success", chunks_added=chunks_added)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/file", response_model=IngestResponse)
async def ingest_file(file: UploadFile = File(...)):
    if not rag_manager.enabled:
        raise HTTPException(
            status_code=400, detail="RAG is not enabled. Please enable RAG first."
        )

    try:
        content = await file.read()

        filename = file.filename or ""
        content_type = file.content_type or ""

        is_pdf = filename.lower().endswith(".pdf") or "application/pdf" in content_type
        if not is_pdf and len(content) >= 4:
            if content[:4] == b"%PDF":
                is_pdf = True

        if is_pdf:
            try:
                import fitz

                pdf_document = fitz.open(stream=content, filetype="pdf")
                text = ""
                for page in pdf_document:
                    text += page.get_text()
                pdf_document.close()
                if not text.strip():
                    raise HTTPException(
                        status_code=400, detail="PDF is empty or could not be read"
                    )
            except ImportError:
                raise HTTPException(
                    status_code=500, detail="PDF processing requires PyMuPDF"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=400, detail=f"Failed to read PDF: {str(e)}"
                )
        else:
            try:
                text = content.decode("utf-8")
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400, detail="File encoding not supported"
                )

        chunks_added = rag_manager.add_documents(
            [text], [{"source": filename or "unknown"}]
        )

        return IngestResponse(status="success", chunks_added=chunks_added)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Session APIs
@app.get("/sessions", response_model=SessionListResponse)
async def get_sessions():
    sessions = session_manager.get_all_sessions()
    return SessionListResponse(sessions=[SessionData(**s) for s in sessions])


@app.post("/sessions")
async def create_session(request: CreateSessionRequest):
    session_id = str(uuid.uuid4())[:8]
    session = session_manager.create_session(session_id, request.name)
    return session


@app.get("/sessions/{session_id}", response_model=SessionData)
async def get_session(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionData(**session)


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    success = session_manager.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "deleted"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
