from typing import Dict, List
from langchain_classic.chat_message_histories.in_memory import ChatMessageHistory
from langchain_classic.memory import ConversationBufferMemory


class InMemoryHistoryManager:
    _instance = None
    _histories: Dict[str, ChatMessageHistory] = {}
    _memories: Dict[str, ConversationBufferMemory] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_session_history(self, session_id: str) -> ConversationBufferMemory:
        if session_id not in self._histories:
            self._histories[session_id] = ChatMessageHistory()

        if session_id not in self._memories:
            self._memories[session_id] = ConversationBufferMemory(
                chat_memory=self._histories[session_id],
                memory_key="history",
                return_messages=True,
            )

        return self._memories[session_id]

    def clear_session(self, session_id: str):
        if session_id in self._histories:
            del self._histories[session_id]
        if session_id in self._memories:
            del self._memories[session_id]

    def get_all_sessions(self) -> List[str]:
        return list(self._histories.keys())


history_manager = InMemoryHistoryManager()
