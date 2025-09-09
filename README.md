# 📚 Document QA Chatbot

An interactive Streamlit chatbot that can answer questions from uploaded documents (PDF, DOCX, Images). Supports multi-step reasoning, tables, code blocks, session history, and chat sharing.

---

## 🧱 Folder Structure

```
qa-bot/
│
├── app/
│   ├── main.py                # Streamlit app UI
│   ├── qa_pipeline.py         # QA logic using LangChain
│   ├── document_processor.py  # Extract text from files
│   ├── history_store.py       # Load/save/delete chat sessions
│   ├── session_manager.py     # Rename, delete, share, download sessions
│   ├── file_manager.py        # Manage uploaded files
│   ├── chat_utils.py          # Answer formatting helpers
│   └── share_handler.py       # Shareable chat sessions
│
├── uploaded/                 # Uploaded files
├── vectorstores/             # FAISS vector databases
├── shared_chats/             # Shared chat history (by token)
├── history/                  # Chat history per session
├── assets/                   # Sample input files (optional)
├── requirements.txt
└── README.md
```

---

## 🚀 Features

✅ Multi-step answers  
✅ Code blocks & tables in markdown  
✅ Image & document OCR  
✅ Session management (rename, delete, download)  
✅ Share sessions with link (`?share=...`)  
✅ Fast loading with embedding caching  

---

## 🛠️ Setup

```bash
# 1. Clone the repo
$ git clone <your-repo>
$ cd qa-bot

# 2. Create virtual environment (optional)
$ python -m venv venv
$ source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
$ pip install -r requirements.txt

# 4. Run the app
$ streamlit run app/main.py
```

---

## 📥 Upload & Ask
- Upload PDF, DOCX, PNG, JPG files.
- Ask questions in plain English.
- Get formatted responses based on extracted content.

---

## 🧪 Example Test Questions

### 🔍 Multi-Step Reasoning
> "Explain the steps involved in the document's process flow."

### 🧾 Tables
> "Can you show a summary of sensors and their types in a table?"

### 💻 Code Understanding
> "What does the function `process_sensor_data()` do in the uploaded file?"

---

## 🧑‍💻 Credit
Built using [LangChain](https://www.langchain.com/), [Streamlit](https://streamlit.io/), [FAISS](https://github.com/facebookresearch/faiss), and [pytesseract](https://github.com/madmaze/pytesseract).

---

## 📬 Feedback / Contributions
Feel free to submit issues, ideas, or improvements via pull requests or discussions.
