======================================================================
🌾 உழவுதளம் (Uzhavuthalam) - Local Multi-PDF Agricultural RAG Application
======================================================================

"உழுதுண்டு வாழ்வாரே வாழ்வார்மற் றெல்லாம் தொழுதுண்டு பின்செல் பவர்" — திருவள்ளுவர்

An intelligent, local Retrieval-Augmented Generation (RAG) assistant designed for farmers, researchers, and agricultural experts. It automatically processes agricultural PDFs, manuals, and market guides, allowing users to query in English, Tamil, or Tanglish and receive precise, context-backed answers strictly in Tamil.

---

### 📂 Project Structure

uzhavuthalam/
│
├── backend/
│   ├── main.py            # FastAPI backend application & endpoints
│   └── rag_engine.py      # LangChain, OpenAI embeddings, FAISS & RAG chain
│
├── frontend/
│   └── app.py             # Streamlit UI with fixed header & Tamil weather widget
│
├── faiss_index/           # Local FAISS vector storage directory (auto-created)
├── Farmer_Img_1.jpg       # Local farmer background wallpaper image
├── requirements.txt       # Python dependencies
└── README.txt             # Project documentation (this file)

---

### 🚀 Tech Stack

* **Backend Framework:** FastAPI, Uvicorn
* **Frontend UI:** Streamlit (Custom CSS agriculture theme & sticky top header)
* **RAG Orchestration:** LangChain
* **Vector Database:** FAISS (Local persistence)
* **LLM & Embeddings:** OpenAI (`gpt-4o-mini`, `text-embedding-3-small`)

---

### ⚙️ Installation & Setup Guide

#### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

#### 2. Clone or Navigate to Project Directory
Open your terminal in the project root folder (`uzhavuthalam/`).

#### 3. Create and Activate Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate