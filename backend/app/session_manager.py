import os
import json
from typing import List, Dict, Optional
from datetime import datetime


class SessionManager:
    _instance = None
    _sessions: Dict[str, Dict] = {}
    _storage_file = "./sessions.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        if os.path.exists(self._storage_file):
            try:
                with open(self._storage_file, "r", encoding="utf-8") as f:
                    self._sessions = json.load(f)
            except:
                self._sessions = {}

    def _save(self):
        with open(self._storage_file, "w", encoding="utf-8") as f:
            json.dump(self._sessions, f, ensure_ascii=False, indent=2)

    def create_session(self, session_id: str, name: Optional[str] = None) -> Dict:
        if session_id not in self._sessions:
            self._sessions[session_id] = {
                "id": session_id,
                "name": name or f"新会话 {len(self._sessions) + 1}",
                "messages": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
            self._save()
        return self._sessions[session_id]

    def get_session(self, session_id: str) -> Optional[Dict]:
        return self._sessions.get(session_id)

    def get_all_sessions(self) -> List[Dict]:
        sessions = list(self._sessions.values())
        sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return sessions

    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self._sessions:
            self.create_session(session_id)

        self._sessions[session_id]["messages"].append(
            {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        )
        self._sessions[session_id]["updated_at"] = datetime.now().isoformat()
        self._save()

    def update_name(self, session_id: str, name: str):
        if session_id in self._sessions:
            self._sessions[session_id]["name"] = name
            self._save()

    def delete_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            self._save()
            return True
        return False

    def clear_all(self):
        self._sessions = {}
        self._save()


session_manager = SessionManager()
