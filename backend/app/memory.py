from typing import Dict, List
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseChatMessageHistory
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory


class InMemoryHistoryManager:
    _instance = None
    _histories: Dict[str, BaseChatMessageHistory] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self._histories:
            self._histories[session_id] = ChatMessageHistory()
        return self._histories[session_id]

    def clear_session(self, session_id: str):
        if session_id in self._histories:
            del self._histories[session_id]

    def get_all_sessions(self) -> List[str]:
        return list(self._histories.keys())


history_manager = InMemoryHistoryManager()
