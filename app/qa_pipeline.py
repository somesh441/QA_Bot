from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from db_handler import get_vectorstore
import time

def get_pipeline():
    return QAWrapper().ask

# --- Prompt Template (multi-step/table/code ready) ---
QA_TEMPLATE = """
You are a helpful assistant. Answer the question based on the given context.

- Use **numbered steps** if the answer involves multiple stages.
- Return **tables** in markdown if helpful.
- If the document contains code, return **code blocks** using triple backticks.
- If you don't know, say so honestly.

Context:
{context}

Question:
{question}
"""

class QAWrapper:
    def __init__(self):
        self.llm = ChatOllama(model="llama3", temperature=0.2)

    def ask(self, query: str):
        vs = get_vectorstore()
        if not vs:
            return {
                "answer": "⚠️ Vectorstore not found. Please upload and process a document first.",
                "sources": []
            }

        retriever = vs.as_retriever()
        prompt = PromptTemplate.from_template(QA_TEMPLATE)

        chain = (
            {"context": retriever, "question": RunnablePassthrough()} |
            prompt |
            self.llm
        )

        # Measure performance
        start = time.time()
        docs = retriever.get_relevant_documents(query)
        retrieval_time = time.time()
        result = chain.invoke(query)
        answer = result.content if hasattr(result, "content") else str(result)

        end = time.time()

        print(f"🔍 Retrieval: {retrieval_time - start:.2f}s | 💬 LLM: {end - retrieval_time:.2f}s")

        sources = list({doc.metadata.get("source", "Unknown") for doc in docs})

        return {
            "answer": answer,
            "sources": sources
        }