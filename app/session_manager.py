from history_store import _history_store
from share_handler import share_handler
import json


def list_sessions():
    return _history_store.list_sessions()


def rename_session(old_id: str, new_id: str):
    _history_store.rename_session(old_id, new_id)


def delete_session(session_id: str):
    _history_store.delete_session(session_id)


def download_session(session_id: str) -> str:
    history = _history_store.load(session_id)
    return json.dumps(history, indent=2, ensure_ascii=False)


def generate_share_link(session_id: str) -> str:
    history = _history_store.load(session_id)
    return share_handler.share_chat_history(session_id, history)