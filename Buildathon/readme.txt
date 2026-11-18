================================================================================
உழவுத்தளம் (UZHAVUTHALAM) - TAMIL NADU AGRICULTURAL SCHEME RAG ASSISTANT
================================================================================

1. OVERVIEW
--------------------------------------------------------------------------------
Uzhavuthalam is a multilingual Retrieval-Augmented Generation (RAG) web 
application built to help farmers in Tamil Nadu discover and understand 
government agricultural schemes, subsidies, and eligibility criteria. 

Users can ask questions in native Tamil script, English, or Tanglish 
(Tamil written in English characters), and the system responds exclusively in 
clear Tamil.

2. KEY FEATURES & ARCHITECTURE
--------------------------------------------------------------------------------
- Split Client-Server Architecture:
  * Backend: FastAPI + Uvicorn serving REST endpoints (/ask, /upload)
  * Frontend: Streamlit web interface with an agricultural theme, live weather 
    card, Thirukural banner, crowd-sourced PDF uploader, and clean source-free 
    chat display.
- Hybrid Retrieval (FAISS + BM25):
  * Dense Vector Search: OpenAI embeddings (text-embedding-3-small) stored in 
    a local FAISS index with cosine relevance score thresholding.
  * Sparse Keyword Search: BM25Retriever initialized dynamically from the 
    FAISS docstore.
  * Rank Fusion: Reciprocal Rank Fusion (RRF) merges semantic and keyword 
    search results for accurate retrieval of scheme acronyms and concepts.
- Cross-Lingual Query Expansion:
  * Translates and expands Tamil, English, and Tanglish queries into bilingual 
    search keywords before retrieval.
- Multi-Layered Safety & Domain Guardrails:
  * Input Safety & Topic Classifier: Blocks illegal acts, political/election 
    controversies, 18+ content, and off-topic queries before retrieval.
  * Relevance Thresholding: Filters low-similarity chunks from FAISS.
  * Strict Tamil Output Enforcement: Programmatically checks Tamil Unicode 
    character ratios (\u0B80-\u0BFF) and enforces translation if English leaks.
- Automated RAG Evaluation:
  * Includes an LLM-as-a-Judge evaluation script measuring Faithfulness, 
    Answer Relevance, Tamil Unicode compliance, and Guardrail blocking accuracy.

3. DIRECTORY STRUCTURE
--------------------------------------------------------------------------------
Buildathon/
├── backend/
│   ├── main.py                  # FastAPI server entry point
│   ├── rag_engine.py            # Hybrid FAISS+BM25 engine & guardrails
│   └── evaluate_rag.py          # Automated RAG & guardrail evaluator
├── frontend/
│   └── app.py                   # Streamlit UI application
├── faiss_index/                 # Local FAISS vector store (auto-generated)
├── Farmer_Img_3.jpg             # Background image for Streamlit UI
├── .env                         # Environment variables (OPENAI_API_KEY)
├── requirements.txt             # Python dependencies
└── readme.txt                   # Project documentation

4. PREREQUISITES & INSTALLATION
--------------------------------------------------------------------------------
Step 1: Create and activate a Python virtual environment (Python 3.10+):
    python -m venv venv
    venv\Scripts\activate          (Windows)

Step 2: Install required dependencies:
    pip install fastapi uvicorn streamlit requests python-dotenv
    pip install langchain langchain-openai langchain-community langchain-text-splitters
    pip install faiss-cpu rank_bm25 pypdf pandas

Step 3: Configure Environment Variables:
    Create a `.env` file in the root directory and add your OpenAI API key:
    OPENAI_API_KEY=your_openai_api_key_here

5. RUNNING THE APPLICATION
--------------------------------------------------------------------------------
You need two terminal windows running simultaneously:

Terminal 1 - Start the FastAPI Backend:
    cd backend
    uvicorn main:app --reload --host 127.0.0.1 --port 8000

Terminal 2 - Start the Streamlit Frontend:
    cd frontend
    streamlit run app.py

Once running, open your browser to:
    http://localhost:8501

6. CROWD-SOURCING PDF DOCUMENTS
--------------------------------------------------------------------------------
- Use the left sidebar ("PDF ஆவணங்களைப் பதிவேற்றுக") in the Streamlit UI to 
  upload agricultural scheme PDFs.
- Uploaded PDFs are automatically split into chunks, embedded, and persisted 
  into the local `faiss_index/` directory for immediate querying.

7. RUNNING AUTOMATED EVALUATION
--------------------------------------------------------------------------------
To benchmark Faithfulness, Answer Relevance, Tamil compliance, and Guardrails:
    cd backend
    python evaluate_rag.py

Results will display in the console and save to `rag_evaluation_report.csv`.
================================================================================