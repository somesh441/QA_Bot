import os
import time
from typing import Optional, Dict
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import torch

BASE_DATA_DIR = "data"
VECTORSTORE_DIR = os.path.join(BASE_DATA_DIR, "vectorstores")
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

# --- Memory cache ---
vectorstore_manager: Dict[str, FAISS] = {}

# --- Embedding model (GPU if available) ---
device = "cuda" if torch.cuda.is_available() else "cpu"
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": device}
)

def get_vectorstore(file_name: str = None) -> Optional[FAISS]:
    if not file_name:
        if vectorstore_manager:
            return next(iter(vectorstore_manager.values()))
        files = [f for f in os.listdir(VECTORSTORE_DIR) if f.endswith(".faiss")]
        if files:
            file_name = files[0].replace(".faiss", "")
        else:
            return None

    if file_name in vectorstore_manager:
        return vectorstore_manager[file_name]

    path = os.path.join(VECTORSTORE_DIR, file_name)
    if os.path.exists(path + ".faiss") and os.path.exists(path + ".pkl"):
        start = time.time()
        vs = FAISS.load_local(path, embedding_model, allow_dangerous_deserialization=True)
        print("Vectorstore loaded in", round(time.time() - start, 2), "sec")
        vectorstore_manager[file_name] = vs
        return vs

    return None

def store_chunks(file_name: str, text: str, chunk_size: int = 400, overlap: int = 40):
    """Split the input text into chunks and store them in a FAISS vectorstore."""
    if not text.strip():
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", " ", ""]
    )

    documents: list[Document] = splitter.create_documents([text], metadatas=[{"source": file_name}])
    if not documents:
        return

    start = time.time()
    vs = FAISS.from_documents(documents, embedding_model)
    print("Embedding + indexing took", round(time.time() - start, 2), "sec")

    path = os.path.join(VECTORSTORE_DIR, file_name)
    vs.save_local(path)
    vectorstore_manager[file_name] = vs
