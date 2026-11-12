import os
import hashlib
import tempfile
from typing import List

import streamlit as st
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

st.set_page_config(page_title="Multi-PDF RAG Assistant", page_icon="📚", layout="wide")
st.title("📚 Multi-PDF RAG Assistant")
st.caption("Ask questions across multiple PDFs and verify every answer against its source.")

with st.sidebar:
    st.header("Configuration")
    # API key is loaded only from the environment or .env file; it is not shown in the UI.
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if api_key:
        st.caption("OpenAI API key loaded from environment configuration.")
    else:
        st.warning("OpenAI API key is not configured. Add OPENAI_API_KEY to your local .env file.")
    chat_model = st.selectbox("Chat model", ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4o"], index=0)
    embedding_model = st.selectbox(
        "Embedding model",
        ["text-embedding-3-small", "text-embedding-3-large"],
        index=0,
    )
    chunk_size = st.slider("Chunk size (characters)", 500, 2000, 1000, 100)
    chunk_overlap = st.slider("Chunk overlap (characters)", 0, 400, 150, 25)
    top_k = st.slider("Retrieved chunks per question", 2, 10, 5)

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = []
if "index_fingerprint" not in st.session_state:
    st.session_state.index_fingerprint = None
if "messages" not in st.session_state:
    st.session_state.messages = []

uploaded_files = st.file_uploader(
    "Upload multiple PDF files",
    type=["pdf"],
    accept_multiple_files=True,
    help="Select several PDFs at once. Each PDF page is indexed with its filename and page number.",
)

def read_uploaded_pdfs(files) -> List[Document]:
    """Save each uploaded PDF temporarily and load one Document per page."""
    all_pages: List[Document] = []
    for uploaded in files:
        raw = uploaded.getvalue()
        if not raw:
            continue
        safe_name = os.path.basename(uploaded.name)
        digest = hashlib.sha256(raw).hexdigest()[:12]
        temp_path = None
        try:
            # Use the platform's temporary directory instead of assuming /tmp exists.
            # Close the file before PyPDFLoader opens it (important on Windows).
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_file.write(raw)
                temp_path = temp_file.name

            pages = PyPDFLoader(temp_path).load()
            for page_doc in pages:
                # PyPDFLoader page metadata is normally zero-based.
                page_index = page_doc.metadata.get("page", 0)
                page_doc.metadata["page_number"] = int(page_index) + 1
                page_doc.metadata["source"] = safe_name
                page_doc.metadata["file_id"] = digest
                all_pages.append(page_doc)
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
    return all_pages

def make_fingerprint(files) -> str:
    h = hashlib.sha256()
    for f in sorted(files, key=lambda x: x.name.lower()):
        h.update(f.name.encode("utf-8"))
        h.update(hashlib.sha256(f.getvalue()).digest())
    return h.hexdigest()

def build_index(files, api_key, embed_model, size, overlap):
    pages = read_uploaded_pdfs(files)
    if not pages:
        raise ValueError("No readable text was found in the uploaded PDFs. They may be empty, damaged, or scanned images without OCR.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=min(overlap, size // 2),
        separators=["\n\n", "\n", ". ", " ", ""],
        add_start_index=True,
    )
    chunks = splitter.split_documents(pages)
    # Keep the page metadata on every chunk, so citations point to the page the text came from.
    embeddings = OpenAIEmbeddings(model=embed_model, api_key=api_key)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore, pages, chunks

if uploaded_files:
    current_fingerprint = make_fingerprint(uploaded_files)
    st.write(f"**Uploaded files:** {len(uploaded_files)}")
    with st.expander("View uploaded filenames", expanded=False):
        for f in uploaded_files:
            st.write(f"📄 {f.name} — {len(f.getvalue()):,} bytes")

    if st.button("🔎 Process PDFs and build shared index", type="primary"):
        if not api_key:
            st.error("OpenAI API key is missing. Add OPENAI_API_KEY=your_key_here to the .env file in the project folder, then restart Streamlit.")
        else:
            try:
                with st.spinner("Reading PDFs, splitting text, creating embeddings, and building the FAISS index..."):
                    vs, pages, chunks = build_index(
                        uploaded_files,
                        api_key,
                        embedding_model,
                        chunk_size,
                        chunk_overlap,
                    )
                st.session_state.vectorstore = vs
                st.session_state.index_fingerprint = current_fingerprint
                st.session_state.indexed_files = [f.name for f in uploaded_files]
                st.session_state.messages = []
                st.success(
                    f"Index ready: {len(uploaded_files)} PDFs, {len(pages)} pages, "
                    f"{len(chunks)} chunks in one FAISS index."
                )
            except Exception as e:
                st.error(f"Could not build the index: {e}")
                st.info("Check that the PDFs contain extractable text, your API key is valid, and your dependencies are installed.")

if st.session_state.vectorstore is not None:
    st.success("FAISS index is ready for questions.")
    st.caption("Indexed files: " + ", ".join(st.session_state.indexed_files))
    if uploaded_files and st.session_state.index_fingerprint != make_fingerprint(uploaded_files):
        st.warning("The uploaded file set has changed since indexing. Click **Process PDFs and build shared index** to refresh the index.")

    st.subheader("Ask your documents")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                with st.expander("Sources and supporting excerpts"):
                    for i, src in enumerate(message["sources"], start=1):
                        st.markdown(f"**[{i}] {src['file']} — page {src['page']}**")
                        st.write(src["excerpt"])

    question = st.chat_input("Ask a question across all indexed PDFs...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        try:
            with st.chat_message("assistant"):
                with st.spinner("Searching documents and preparing an answer..."):
                    retriever = st.session_state.vectorstore.as_retriever(
                        search_type="similarity",
                        search_kwargs={"k": top_k},
                    )
                    docs = retriever.invoke(question)

                    if not docs:
                        answer = "I couldn't find relevant passages in the indexed documents."
                        sources = []
                    else:
                        context_parts = []
                        sources = []
                        for source_num, doc in enumerate(docs, start=1):
                            filename = doc.metadata.get("source", "Unknown file")
                            page = doc.metadata.get("page_number", doc.metadata.get("page", "Unknown"))
                            excerpt = " ".join(doc.page_content.split())
                            context_parts.append(
                                f"[{source_num}] Source: {filename}, page {page}\\n{doc.page_content}"
                            )
                            sources.append({
                                "file": filename,
                                "page": page,
                                "excerpt": excerpt[:700] + ("…" if len(excerpt) > 700 else ""),
                            })

                        prompt = ChatPromptTemplate.from_messages([
                            ("system",
                             "You answer questions using only the supplied document context. "
                             "If the context does not support an answer, say you could not find enough "
                             "evidence in the uploaded PDFs. Do not invent facts or citations. "
                             "Cite claims inline using [1], [2], etc., matching the numbered source list "
                             "provided after the context. If sources disagree, describe the disagreement."),
                            ("human", "Question:\n{question}\n\nDocument context:\n{context}\n\n"
                                      "Available source labels:\n{source_labels}\n\n"
                                      "Answer clearly and cite supported claims inline.")
                        ])
                        source_labels = "\n".join(
                            f"[{i}] {s['file']} — page {s['page']}" for i, s in enumerate(sources, start=1)
                        )
                        llm = ChatOpenAI(model=chat_model, temperature=0, api_key=api_key)
                        chain = prompt | llm | StrOutputParser()
                        answer = chain.invoke({
                            "question": question,
                            "context": "\n\n---\n\n".join(context_parts),
                            "source_labels": source_labels,
                        })

                    st.markdown(answer)
                    if sources:
                        with st.expander("Sources and supporting excerpts", expanded=True):
                            for i, src in enumerate(sources, start=1):
                                st.markdown(f"**[{i}] {src['file']} — page {src['page']}**")
                                st.write(src["excerpt"])
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    })
        except Exception as e:
            st.error(f"Question answering failed: {e}")
            st.info("Verify the OpenAI API key, model access, and network connection.")

    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()
else:
    st.info("Upload PDFs, then click **Process PDFs and build shared index** to start asking questions.")

with st.expander("Important notes"):
    st.markdown(
        "- This starter app builds one in-memory FAISS index from all uploaded PDFs in the current Streamlit session.\n"
        "- Page numbers shown are human-readable PDF page numbers starting at 1.\n"
        "- Scanned PDFs may need OCR before indexing; this app does not perform OCR.\n"
        "- Uploaded content is sent to the configured OpenAI API for embeddings and answer generation. Do not upload confidential documents unless your organization's policies allow it.\n"
        "- For production use, add authentication, upload-size limits, persistent index storage, logging, and tests."
    )
