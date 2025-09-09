import streamlit as st
from datetime import datetime
import pdfplumber
from docx import Document as DocxDocument
from PIL import Image
import pytesseract
import os
import re
import json

from qa_pipeline import get_pipeline
from db_handler import vectorstore_manager, store_chunks
from history_store import save_history, load_history, _history_store
from share_handler import init_share_handler

# --- Ensure upload & vectorstore folders exist ---
os.makedirs("uploaded", exist_ok=True)
os.makedirs("vectorstores", exist_ok=True)

# --- Streamlit Config ---
st.set_page_config(page_title="📚 Doc QA Bot", layout="wide")

# --- Shared Session Load ---
share_token = st.query_params.get("share")
shared = None
if share_token:
    shared = init_share_handler().load_shared_chat_history(share_token)
    if shared:
        st.info("🔗 You are viewing a shared chat session.")
    else:
        st.error("❌ Invalid or expired share link.")

# --- Session Initialization ---
if "chat_id" not in st.session_state:
    if shared:
        st.session_state.chat_id = shared["metadata"]["chat_id"]
    else:
        st.session_state.chat_id = datetime.now().strftime("%Y%m%d%H%M%S")

if "chat_history" not in st.session_state:
    if shared:
        st.session_state.chat_history = shared["messages"]
    else:
        st.session_state.chat_history = load_history(st.session_state.chat_id)

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# --- Sidebar: Upload + Controls ---
st.sidebar.title("Upload Documents")
uploaded_files = st.sidebar.file_uploader(
    "Upload PDFs, DOCX, TXT, Images",
    type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

st.sidebar.markdown("### Uploaded Files")
remove_file = st.sidebar.radio("🗑️ Select file to delete", ["None"] + st.session_state.uploaded_files, index=0)
if remove_file != "None":
    try:
        os.remove(os.path.join("uploaded", remove_file))
        st.session_state.uploaded_files.remove(remove_file)
        st.success(f"Removed {remove_file}")
    except Exception as e:
        st.error(f"Error deleting file: {e}")

if st.sidebar.button("➕ New Chat"):
    st.session_state.chat_id = datetime.now().strftime("%Y%m%d%H%M%S")
    st.session_state.chat_history = []
    save_history(st.session_state.chat_id, [])
    st.rerun()

if st.sidebar.button("🗑️ Clear History"):
    st.session_state.chat_history = []
    save_history(st.session_state.chat_id, [])
    st.success("Chat history cleared.")

# Session Selector
session_list = _history_store.list_sessions()
selected_session = st.sidebar.selectbox("💬 View Previous Sessions", session_list, index=session_list.index(st.session_state.chat_id) if st.session_state.chat_id in session_list else 0)
if selected_session != st.session_state.chat_id:
    st.session_state.chat_id = selected_session
    st.session_state.chat_history = load_history(selected_session)

# Session Tools
with st.sidebar.expander("⚙️ Manage Session"):
    new_name = st.text_input("Rename session", value=st.session_state.chat_id)
    if st.button("Rename"):
        _history_store.rename_session(st.session_state.chat_id, new_name)
        st.session_state.chat_id = new_name
        st.rerun()

    if st.button("Delete"):
        _history_store.delete_session(st.session_state.chat_id)
        st.session_state.chat_history = []
        st.session_state.chat_id = datetime.now().strftime("%Y%m%d%H%M%S")
        st.rerun()

    if st.button("Download Chat"):
        raw = json.dumps(st.session_state.chat_history, indent=2)
        st.download_button("📥 Download", raw, file_name=f"{st.session_state.chat_id}.json")

    # --- Share Chat Button ---
    if st.button("🔗 Share Chat"):
        token = init_share_handler().share_chat_history(st.session_state.chat_id)
        
        # 🔧 Replace this with your actual deployed base URL if needed
        BASE_URL = "http://localhost:8501"  # ✅ ← change this when deployed
        share_url = f"{BASE_URL}?share={token}"
        
        st.session_state.share_url = share_url

# --- Display Shareable Link ---
if "share_url" in st.session_state:
    st.sidebar.markdown("✅ **Shareable Link Generated**")
    st.sidebar.text_input("Copy this link:", value=st.session_state.share_url, key="copy_share_link")

# --- Utility: Sanitize Filename ---
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|\x00]', "_", name)

# --- Save Uploaded Files + Chunk ---
for uploaded_file in uploaded_files:
    safe_name = sanitize_filename(uploaded_file.name)
    file_path = os.path.join("uploaded", safe_name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    if safe_name not in st.session_state.uploaded_files:
        st.session_state.uploaded_files.append(safe_name)
        ext = safe_name.split(".")[-1].lower()

        if ext == "pdf":
            with pdfplumber.open(file_path) as pdf:
                text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        elif ext == "docx":
            doc = DocxDocument(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif ext == "txt":
            with open(file_path, "r", encoding="utf-8") as txt_file:
                text = txt_file.read()
        elif ext in ["png", "jpg", "jpeg"]:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
        else:
            text = ""

        store_chunks(safe_name, text)

# --- Title ---
st.title("👩‍💼 Document QA Chatbot")

# --- Chat Input ---
question = st.text_input("Ask a question about your document:", key="user_input")
pipeline = get_pipeline()
if st.button("Ask") and question:
    with st.spinner("Finding answers..."):
        answers = pipeline(question)
        st.session_state.chat_history.insert(0, {
            "question": question,
            "answer": answers.get("answer", "No answer found."),
            "sources": answers.get("sources", [])
        })
        save_history(st.session_state.chat_id, st.session_state.chat_history)

# --- Chat History Display ---
for qa in st.session_state.chat_history:
    st.markdown(f"**Q:** {qa['question']}")
    st.markdown("**A:**")
    st.markdown(str(qa['answer']), unsafe_allow_html=True)
    if qa.get("sources"):
        st.markdown("_Sources:_")
        for src in qa["sources"]:
            st.markdown(f"- {src}")
