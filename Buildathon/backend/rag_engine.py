import os
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

INDEX_PATH = "faiss_index"
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

def get_vector_store():
    if os.path.exists(INDEX_PATH):
        return FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    return None

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
        
        # 1. Multilingual Expansion (Tamil Script, English, Tanglish -> English Keywords)
        translation_prompt = (
            "You are a multilingual AI assistant for Tamil Nadu agriculture. "
            "The user query may be written in Tamil script, English, or Tanglish (Tamil words written in English letters). "
            "Extract, translate, or expand the query into clear English search keywords and phrases "
            "so it matches the indexed agricultural scheme documents in FAISS, while retaining core terms. "
            "Return ONLY the translated/expanded search query text.\n\n"
            f"User Query: {question}"
        )
        search_query = llm.invoke(translation_prompt).content.strip()
        print(f"🔍 User Query: {question} | Expanded Search Query: {search_query}")

        # 2. Configure MMR Retriever
        retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 6, "fetch_k": 25, "lambda_mult": 0.7}
        )
        
        retrieved_docs = retriever.invoke(search_query)
        sources = list(set([doc.metadata.get("source", "Unknown") for doc in retrieved_docs]))
        
        # 3. Construct Direct LCEL Chain for Generation (Strict Tamil Output)
        system_prompt = (
            "நீங்கள் 'உழவுத்தளம்' (Uzhavuthalam) என்ற தமிழ் விவசாய உதவி AI உதவியாளர் ஆவீர்கள்.\n"
            "வழங்கப்பட்ட சூழல் (Context) மற்றும் ஆவணங்களின் அடிப்படையில் விவசாயிகளுக்கு தெளிவான, பயனுள்ள பதில்களை வழங்கவும்.\n"
            "கட்டாயம் **தமிழில் மட்டுமே** பதிலளிக்க வேண்டும். ஆங்கிலத்திலோ அல்லது பிற மொழிகளிலோ பதிலளிக்கக் கூடாது.\n\n"
            "சூழல்:\n{context}"
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "User Question: {input}\n\nRelevant Context Provided Above."),
        ])
        
        # Format retrieved context
        context_text = format_docs(retrieved_docs)
        
        # Execute chain invocation
        chain = prompt | llm | StrOutputParser()
        answer_text = chain.invoke({"context": context_text, "input": question})
        
        if not answer_text.strip():
            answer_text = "மன்னிக்கவும், தங்களால் கேட்கப்பட்ட கேள்விக்கான பதில் கிடைக்கவில்லை."
        
        return {
            "answer": answer_text,
            "sources": sources
        }
    except Exception as e:
        print(f"⚠️ Error in query_rag: {e}")
        return {
            "answer": f"பிழை ஏற்பட்டுள்ளது: {str(e)}",
            "sources": []
        }