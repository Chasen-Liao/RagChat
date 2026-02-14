from typing import AsyncGenerator, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from .config import settings


class ChatHistory:
    _instance = None
    _histories = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_messages(self, session_id: str) -> List:
        if session_id not in self._histories:
            self._histories[session_id] = [
                SystemMessage(
                    content="你是一个专业的AI助手，名叫小正。你知识渊博，回答准确、详细、有帮助。使用中文回答，语气友好专业。"
                )
            ]
        return self._histories[session_id]

    def add_message(self, session_id: str, role: str, content: str):
        messages = self.get_messages(session_id)
        if role == "user":
            messages.append(HumanMessage(content=content))
        else:
            messages.append(AIMessage(content=content))

    def clear_session(self, session_id: str):
        if session_id in self._histories:
            del self._histories[session_id]

    def get_all_sessions(self):
        return list(self._histories.keys())


history_manager = ChatHistory()


def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        api_key=settings.siliconflow_api_key,
        base_url=settings.siliconflow_api_base,
        model=settings.llm_model,
        streaming=True,
        temperature=0.7,
    )


async def stream_chat(
    query: str, session_id: str = "default"
) -> AsyncGenerator[str, None]:
    llm = get_llm()
    history_manager.add_message(session_id, "user", query)
    messages = history_manager.get_messages(session_id)

    async for chunk in llm.astream(messages):
        if chunk.content:
            yield chunk.content

    full_response = ""
    async for chunk in llm.astream(messages):
        if chunk.content:
            full_response += chunk.content
    history_manager.add_message(session_id, "assistant", full_response)


def chat(query: str, session_id: str = "default") -> dict:
    llm = get_llm()
    history_manager.add_message(session_id, "user", query)
    messages = history_manager.get_messages(session_id)

    response = llm.invoke(messages)
    answer = response.content

    history_manager.add_message(session_id, "assistant", answer)

    return {"answer": answer, "sources": []}
