import os
import certifi
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Fix SSL certificate verification for Windows
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

from dotenv import load_dotenv
load_dotenv()

# LangChain & FAISS imports
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

INDEX_PATH = "faiss_index"

def scrape_and_index_tn_schemes(dep_url="https://www.tn.gov.in/scheme_list.php?dep_id=Mg=="):
    print("Step 1: Scraping all Tamil Nadu Agricultural Scheme links...")
    
    try:
        response = requests.get(dep_url, headers={"User-Agent": os.environ["USER_AGENT"]}, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"⚠️ Error fetching main page: {e}")
        return {"status": "error", "message": str(e)}

    soup = BeautifulSoup(response.text, 'html.parser')

    scheme_links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href'].strip()
        if "scheme_details.php" in href or "scheme" in href.lower():
            full_url = urljoin(dep_url, href)
            scheme_links.add(full_url)

    scheme_links = list(scheme_links)
    print(f"Found {len(scheme_links)} unique scheme links. Loading content for all documents...")

    # Load all scheme documents using WebBaseLoader
    all_documents = []
    title_mapping = {}

    for i, link in enumerate(scheme_links):
        print(f"[{i+1}/{len(scheme_links)}] Loading: {link}")
        try:
            loader = WebBaseLoader(link)
            docs = loader.load()
            for doc in docs:
                title = doc.metadata.get("title", f"TN Agri Scheme {i+1}")
                title_mapping[link] = title
                all_documents.append(doc)
        except Exception as e:
            print(f"  -> Error loading {link}: {e}")

    print(f"\nSuccessfully loaded {len(all_documents)} raw web documents.")

    if not all_documents:
        print("⚠️ No valid document content extracted.")
        return {"status": "warning", "message": "No document content could be extracted."}

    formatted_documents = []

    for doc in all_documents:
        source_url = doc.metadata.get("source", "")
        scheme_title = title_mapping.get(source_url, "Tamil Nadu Agricultural Scheme")
        page_text = doc.page_content.strip()

        if len(page_text) > 80:
            formatted_doc = Document(
                page_content=f"Scheme Title: {scheme_title}\n\nContent:\n{page_text}",
                metadata={"source": source_url, "title": scheme_title}
            )
            formatted_documents.append(formatted_doc)

    # Step 2: Split text chunks and index into FAISS Vector Store
    print("Splitting text documents into chunks for vector indexing...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(formatted_documents)
    
    print("Initializing OpenAI Embeddings (text-embedding-3-small)...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    if os.path.exists(INDEX_PATH):
        print("📂 Loading existing FAISS vector store...")
        vector_store = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        vector_store.add_documents(chunks)
    else:
        print("📂 Creating new FAISS vector store...")
        vector_store = FAISS.from_documents(chunks, embeddings)
        
    vector_store.save_local(INDEX_PATH)
    print(f"✅ Success! Added {len(chunks)} text chunks from {len(formatted_documents)} web schemes into FAISS vector database.")
    
    return {
        "status": "success", 
        "schemes_scraped": len(formatted_documents), 
        "chunks_added": len(chunks)
    }

if __name__ == "__main__":
    scrape_and_index_tn_schemes()