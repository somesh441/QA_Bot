import os
import json
import uuid
from typing import Dict

class ShareHandler:
    def __init__(self, share_dir: str = "shared_chats"):
        self.share_dir = share_dir
        os.makedirs(self.share_dir, exist_ok=True)

    def _get_path(self, token: str) -> str:
        return os.path.join(self.share_dir, f"{token}.json")

    def share_chat_history(self, chat_id: str, messages: list = None) -> str:
        from history_store import load_history  # Prevent circular import
        if messages is None:
            messages = load_history(chat_id)

        token = str(uuid.uuid4())
        data = {
            "metadata": {"chat_id": chat_id},
            "messages": messages
        }

        with open(self._get_path(token), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return token

    def load_shared_chat_history(self, token: str) -> Dict:
        try:
            with open(self._get_path(token), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load shared chat: {e}")
            return {}


# 🔧 Global instance
share_handler = ShareHandler()

def init_share_handler() -> ShareHandler:
    return share_handler
