# Multi-PDF RAG Assistant (LangChain + Streamlit + FAISS)

A starter app that lets users upload several PDFs, creates a single FAISS vector index, and answers questions using retrieved passages with filename and page citations.

## Features

- Upload multiple PDFs in one session
- Extract text page-by-page and preserve source metadata
- Split text into overlapping chunks
- Embed chunks using OpenAI embeddings
- Store all chunks in one FAISS index
- Ask questions across the whole indexed set
- Show inline source markers and expandable filename/page excerpts

## Requirements

- Python 3.10 or newer
- OpenAI API key with access to the selected chat and embedding models
- Internet connection for OpenAI API calls

## Setup (Windows PowerShell)

```powershell
cd multi_pdf_rag_app
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and replace the placeholder with your API key:

```text
OPENAI_API_KEY=your_real_key_here
```

Keep `.env` private. Do not commit it to Git or share it.

## Run

```powershell
streamlit run app.py
```

Streamlit opens the app in your browser. Upload multiple PDFs, click **Process PDFs and build shared index**, then ask a question.

## Setup (macOS / Linux)

```bash
cd multi_pdf_rag_app
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your API key
streamlit run app.py
```

## How source citations work

The PDF loader creates one LangChain `Document` per page. The app adds:
- `source`: original filename
- `page_number`: human-readable page number starting at 1
- `file_id`: content hash for distinguishing uploads

The splitter carries page metadata to each chunk. Retrieved passages are shown with the filename and page number.

## Notes and limitations

- The FAISS index is in memory and is not persisted after the Streamlit session/server restarts.
- The app rebuilds the index when the user clicks the processing button. If uploads change after indexing, the UI warns that the index should be refreshed.
- Scanned/image-only PDFs need OCR before this app can retrieve their text.
- This starter app uses similarity search; hybrid search, reranking, conversational memory, and automated evaluation can be added later.
- OpenAI API usage may incur charges. Documents are sent to OpenAI for embeddings and answer generation.
- Do not use the app with confidential or regulated files unless the chosen hosting, retention, and API settings meet your organization's requirements.

## Suggested production improvements

1. Add authentication and authorization.
2. Add upload size, page-count, and file-count limits.
3. Persist FAISS indexes per user or workspace and prevent cross-user retrieval.
4. Add OCR for scanned PDFs.
5. Add a reranker and retrieval evaluation tests.
6. Add deletion controls and lifecycle policies for stored documents.
7. Test citations with adversarial questions and verify that every cited claim is supported by its referenced page.
