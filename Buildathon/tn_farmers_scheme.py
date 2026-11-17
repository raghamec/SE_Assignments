import os
from typing import List
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

FAISS_INDEX_PATH = "faiss_index"
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

def process_and_store_pdfs(file_paths: List[str]) -> int:
    """Loads multiple PDFs, splits them, and saves/merges into local FAISS."""
    all_docs = []
    for path in file_paths:
        loader = PyPDFLoader(path)
        all_docs.extend(loader.load())

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )
    chunks = text_splitter.split_documents(all_docs)

    # Load existing index and merge, or create a new one
    if os.path.exists(FAISS_INDEX_PATH):
        vector_store = FAISS.load_local(
            FAISS_INDEX_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        vector_store.add_documents(chunks)
    else:
        vector_store = FAISS.from_documents(chunks, embeddings)

    vector_store.save_local(FAISS_INDEX_PATH)
    return len(chunks)

def query_rag(question: str) -> dict:
    """Retrieves relevant chunks from local FAISS and generates an answer."""
    if not os.path.exists(FAISS_INDEX_PATH):
        return {"answer": "No documents indexed yet. Please upload PDFs first.", "sources": []}

    vector_store = FAISS.load_local(
        FAISS_INDEX_PATH, 
        embeddings, 
        allow_dangerous_deserialization=True
    )
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})
    retrieved_docs = retriever.invoke(question)

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = ChatPromptTemplate.from_template("""
    Answer the question based strictly on the provided context. 
    If the answer is not in the context, state that you don't know.

    Context:
    {context}

    Question: {question}
    """)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": lambda _: format_docs(retrieved_docs), "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    answer = chain.invoke(question)
    
    # Extract unique source filenames and page numbers
    sources = list({
        f"{os.path.basename(doc.metadata.get('source', 'Unknown'))} (Page {doc.metadata.get('page', 0) + 1})"
        for doc in retrieved_docs
    })

    return {"answer": answer, "sources": sources}