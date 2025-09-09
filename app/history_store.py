import os
import json
from typing import List, Dict

class HistoryStore:
    def __init__(self, persist_dir: str = "chat_histories"):
        self.persist_dir = persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)

    def get_path(self, session_id: str) -> str:
        return os.path.join(self.persist_dir, f"{session_id}.json")

    def load(self, session_id: str) -> List[Dict]:
        try:
            with open(self.get_path(session_id), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save(self, session_id: str, history: List[Dict]):
        try:
            with open(self.get_path(session_id), "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Saving chat history failed: {str(e)}")

    def clear(self, session_id: str):
        try:
            os.remove(self.get_path(session_id))
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"[ERROR] Clearing history failed: {e}")

    def list_sessions(self) -> List[str]:
        return [
            f[:-5] for f in os.listdir(self.persist_dir)
            if f.endswith(".json")
        ]

    def rename_session(self, old_id: str, new_id: str):
        old_path = self.get_path(old_id)
        new_path = self.get_path(new_id)
        if os.path.exists(old_path):
            os.rename(old_path, new_path)

    def delete_session(self, session_id: str):
        self.clear(session_id)


# ✅ Exported for app use
_history_store = HistoryStore()

def save_history(session_id: str, history: List[Dict]):
    _history_store.save(session_id, history)

def load_history(session_id: str) -> List[Dict]:
    return _history_store.load(session_id)

def list_all_sessions() -> List[str]:
    return _history_store.list_sessions()

def clear_history(session_id: str):
    _history_store.clear(session_id)