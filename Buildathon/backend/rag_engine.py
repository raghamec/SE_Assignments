import os
import re
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

INDEX_PATH = "faiss_index"
RELEVANCE_THRESHOLD = 0.35  # Minimum FAISS normalized relevance score
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

def get_vector_store():
    if os.path.exists(INDEX_PATH):
        return FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    return None

def get_all_docs_from_faiss(vector_store) -> List[Document]:
    """Extracts all Document chunks stored inside the FAISS docstore for BM25 indexing."""
    if not vector_store or not hasattr(vector_store, "docstore"):
        return []
    return list(vector_store.docstore._dict.values())

# --- GUARDRAIL 1: ENHANCED INPUT / DOMAIN TOPIC & SAFETY CLASSIFICATION ---
def is_safe_and_on_topic(llm: ChatOpenAI, question: str) -> str:
    """
    Classifies user input to ensure it is strictly related to agriculture/schemes 
    AND explicitly filters out illegal activities, political tension, and 18+ content.
    """
    guard_prompt = (
        "You are a strict safety and domain guardrail classifier for 'Uzhavuthalam', a Tamil Nadu agricultural assistant chatbot. "
        "Analyze the user input and check against these rules:\n"
        "1. BLOCK (Return 'UNSAFE') if the query contains or asks about: illegal acts, weapons, drugs, political controversies, elections, political parties, hate speech, violence, or 18+ adult/explicit content.\n"
        "2. ALLOW (Return 'YES') if the query is about agriculture, farming, crops, irrigation, livestock, weather for farming, or Tamil Nadu government farming schemes/subsidies.\n"
        "3. GREETING (Return 'GREETING') if it's a simple greeting like 'vanakkam', 'hello', or 'hi'.\n"
        "4. OFF-TOPIC (Return 'NO') if it's unrelated to agriculture (e.g., coding, movie reviews, general tech, non-farming topics).\n\n"
        "Reply strictly with ONLY one word: YES, UNSAFE, NO, or GREETING.\n\n"
        f"User Input: {question}"
    )
    verdict = llm.invoke(guard_prompt).content.strip().upper()
    print(f"🛡️ Advanced Safety Guardrail Verdict: {verdict}")
    return verdict

# --- GUARDRAIL 2: HYBRID RETRIEVAL WITH SCORE THRESHOLDING ---
def hybrid_retrieve(vector_store, query: str, k: int = 6) -> List[Document]:
    """
    Combines FAISS dense vector search (filtered by relevance threshold) with BM25 sparse keyword search
    using Reciprocal Rank Fusion (RRF).
    """
    docs_with_scores = vector_store.similarity_search_with_relevance_scores(query, k=15)
    filtered_faiss_docs = [
        doc for doc, score in docs_with_scores if score >= RELEVANCE_THRESHOLD
    ][:k]

    all_docs = get_all_docs_from_faiss(vector_store)
    if not all_docs:
        return filtered_faiss_docs

    bm25_retriever = BM25Retriever.from_documents(all_docs)
    bm25_retriever.k = k
    bm25_docs = bm25_retriever.invoke(query)

    rrf_scores = {}
    doc_map = {}
    rrf_k = 60

    for rank, doc in enumerate(filtered_faiss_docs):
        key = doc.page_content
        doc_map[key] = doc
        rrf_scores[key] = rrf_scores.get(key, 0.0) + (0.6 / (rank + rrf_k))

    for rank, doc in enumerate(bm25_docs):
        key = doc.page_content
        doc_map[key] = doc
        rrf_scores[key] = rrf_scores.get(key, 0.0) + (0.4 / (rank + rrf_k))

    sorted_keys = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
    return [doc_map[key] for key in sorted_keys[:k]]

# --- GUARDRAIL 3: OUTPUT LANGUAGE VERIFICATION ---
def ensure_tamil_output(llm: ChatOpenAI, text: str) -> str:
    """
    Programmatically verifies that the output contains sufficient Tamil Unicode characters
    (\u0B80 - \u0BFF). If English/non-Tamil text dominates, enforces a strict Tamil translation.
    """
    tamil_chars = re.findall(r'[\u0B80-\u0BFF]', text)
    alpha_chars = re.findall(r'[a-zA-Z]', text)

    if len(alpha_chars) > len(tamil_chars):
        print("🛡️ Output Language Guardrail Triggered: Enforcing strict Tamil translation.")
        fix_prompt = (
            "Translate the following agricultural response completely into natural, clear Tamil script. "
            "Do NOT include English sentences. Retain official scheme acronyms in Tamil transliteration if needed.\n\n"
            f"Text:\n{text}"
        )
        return llm.invoke(fix_prompt).content.strip()
    return text

def process_and_store_pdfs(file_paths: List[str]) -> int:
    documents = []
    for path in file_paths:
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(path)
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = os.path.basename(path)
            documents.append(doc)
            
    if not documents:
        return 0
        
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    
    vector_store = get_vector_store()
    if vector_store:
        vector_store.add_documents(chunks)
    else:
        vector_store = FAISS.from_documents(chunks, embeddings)
        
    vector_store.save_local(INDEX_PATH)
    return len(chunks)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def query_rag(question: str):
    try:
        vector_store = get_vector_store()
        if not vector_store:
            return {
                "answer": "மன்னிக்கவும், தரவுத்தளம் (FAISS Index) கிடைக்கவில்லை. தயவுசெய்து ஆவணங்களைப் பதிவேற்றவும் அல்லது அரசு திட்டங்களை ஸ்கிரேப் செய்யவும்.",
                "sources": []
            }
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

        # 1. Execute Enhanced Safety & Topic Classifier Guardrail
        safety_status = is_safe_and_on_topic(llm, question)
        
        if safety_status == "UNSAFE":
            return {
                "answer": "மன்னிக்கவும், அரசியல், சட்டவிரோதமான செயல்கள் அல்லது வயதுக்குட்பட்ட (18+) உள்ளடக்கம் குறித்த கேள்விகளுக்கு என்னால் பதிலளிக்க முடியாது. நான் விவசாயம் மற்றும் அரசு திட்டங்கள் குறித்த உதவிகளுக்காக மட்டுமே உருவாக்கப்பட்டுள்ளேன்.",
                "sources": []
            }
        elif safety_status == "GREETING":
            return {
                "answer": "வணக்கம்! நான் 'உழவுத்தளம்' வேளாண் உதவி AI. தமிழ்நாடு அரசு வேளாண் திட்டங்கள், மானியங்கள் மற்றும் விவசாயம் தொடர்பான உங்கள் கேள்விகளைக் கேளுங்கள்.",
                "sources": []
            }
        elif safety_status != "YES":
            return {
                "answer": "மன்னிக்கவும், நான் விவசாயம் மற்றும் தமிழ்நாடு அரசு வேளாண் திட்டங்கள் தொடர்பான கேள்விகளுக்கு மட்டுமே பதிலளிக்க வடிவமைக்கப்பட்டுள்ளேன்.",
                "sources": []
            }
        
        # 2. Multilingual Expansion
        translation_prompt = (
            "You are an expert search query expansion assistant for Tamil Nadu agriculture. "
            "The user query may be in Tamil script, English, or Tanglish. "
            "Your job is to generate a comprehensive search query combining:\n"
            "1. The original Tamil keywords.\n"
            "2. Standard English agriculture/scheme terminology (e.g., 'micro irrigation', 'PMKSY', 'subsidy', 'drip irrigation').\n"
            "Return ONLY the expanded bilingual search query string.\n\n"
            f"User Query: {question}"
        )
        search_query = llm.invoke(translation_prompt).content.strip()
        print(f"🔍 User Query: {question} | Expanded Search Query: {search_query}")

        # 3. Hybrid Retrieval
        retrieved_docs = hybrid_retrieve(vector_store, search_query, k=6)
        sources = list(set([doc.metadata.get("source", "Unknown") for doc in retrieved_docs]))
        
        # 4. Strict System Prompt Rules for Safety, Politics, and Tone
        system_prompt = (
            "நீங்கள் 'உழவுத்தளம்' (Uzhavuthalam) என்ற தமிழ் விவசாய உதவி AI உதவியாளர் ஆவீர்கள்.\n"
            "வழங்கப்பட்ட சூழல் (Context) மற்றும் ஆவணங்களின் அடிப்படையில் விவசாயிகளுக்கு தெளிவான, பயனுள்ள பதில்களை வழங்கவும்.\n\n"
            "முக்கிய பாதுகாப்பு விதிகள் (Core Safety Rules):\n"
            "- எக்காரணம் கொண்டும் அரசியல் கட்சிகள், தலைவர்கள், தேர்தல் விவாதங்கள் அல்லது சமூக பதட்டங்கள் தொடர்பான கருத்துக்களைத் தவிர்க்கவும்.\n"
            "- சட்டவிரோத செயல்கள், வன்முறை அல்லது 18+ வயதுக்குட்பட்ட எந்தவொரு தகவலையும் எந்த சூழ்நிலையிலும் பரிந்துரைக்கக் கூடாது.\n"
            "- கட்டாயம் **தமிழில் மட்டுமே** பதிலளிக்க வேண்டும்.\n\n"
            "சூழல்:\n{context}"
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "User Question: {input}\n\nRelevant Context Provided Above."),
        ])
        
        context_text = format_docs(retrieved_docs)
        chain = prompt | llm | StrOutputParser()
        raw_answer = chain.invoke({"context": context_text, "input": question})
        
        # 5. Enforce Tamil Unicode Output Verification
        final_answer = ensure_tamil_output(llm, raw_answer)
        
        if not final_answer.strip():
            final_answer = "மன்னிக்கவும், தங்களால் கேட்கப்பட்ட கேள்விக்கான பதில் கிடைக்கவில்லை."
        
        return {
            "answer": final_answer,
            "sources": sources
        }
    except Exception as e:
        print(f"⚠️ Error in query_rag: {e}")
        return {
            "answer": f"பிழை ஏற்பட்டுள்ளது: {str(e)}",
            "sources": []
        }