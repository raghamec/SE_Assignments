import os
import shutil
import tempfile
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from .rag_engine import process_and_store_pdfs, query_rag
from .scraper import scrape_and_index_tn_schemes    

app = FastAPI(title="Local Multi-PDF RAG API")

class QueryRequest(BaseModel):
    question: str

@app.post("/upload")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    saved_paths = []
    
    try:
        for file in files:
            if not file.filename.endswith(".pdf"):
                raise HTTPException(status_code=400, detail=f"{file.filename} is not a PDF.")
            
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_paths.append(file_path)

        chunks_added = process_and_store_pdfs(saved_paths)
        return {
            "message": f"Successfully processed {len(files)} PDF(s).",
            "chunks_indexed": chunks_added
        }
    finally:
        shutil.rmtree(temp_dir)

@app.post("/ask")
async def ask_question(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    return query_rag(request.question)

# @app.post("/scrape-schemes")
# def trigger_scraper():
#     result = scrape_and_index_tn_schemes()
#     return result


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)