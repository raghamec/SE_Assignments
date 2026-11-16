import os
import certifi
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Fix SSL certificate verification for Windows
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

load_dotenv()

from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain

def build_and_store_neo4j_graph():
    print("Step 1: Scraping all Tamil Nadu Agricultural Schemes...")
    main_url = "https://www.tn.gov.in/scheme_list.php?dep_id=Mg=="
    response = requests.get(main_url, headers={"User-Agent": os.environ["USER_AGENT"]})
    soup = BeautifulSoup(response.text, 'html.parser')

    scheme_links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if "scheme_details.php" in href or "scheme" in href.lower():
            full_url = urljoin(main_url, href)
            scheme_links.add(full_url)

    scheme_links = list(scheme_links)
    print(f"Found {len(scheme_links)} unique scheme links. Loading content for ALL documents...")

    # Load all scheme documents
    all_documents = []
    for i, link in enumerate(scheme_links):
        print(f"[{i+1}/{len(scheme_links)}] Loading: {link}")
        try:
            loader = WebBaseLoader(link)
            docs = loader.load()
            all_documents.extend(docs)
        except Exception as e:
            print(f"  -> Error loading {link}: {e}")

    print(f"\nSuccessfully loaded {len(all_documents)} documents.")

    # Step 2 & 3: Extract graph entities using LLM in batches (to manage token limits safely)
    print("Initializing LLM Graph Transformer...")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_transformer = LLMGraphTransformer(llm=llm)

    batch_size = 10
    all_graph_documents = []
    print(f"Extracting entities and relationships across {len(all_documents)} documents in batches...")
    
    for i in range(0, len(all_documents), batch_size):
        batch = all_documents[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1} ({len(batch)} documents)...")
        try:
            g_docs = llm_transformer.convert_to_graph_documents(batch)
            all_graph_documents.extend(g_docs)
        except Exception as e:
            print(f"  -> Error in batch extraction: {e}")

    # Step 4: Connect to Neo4j Aura and Store
    print("\nConnecting to Neo4j Aura...")
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD")
    )

    print(f"Saving {len(all_graph_documents)} graph document structures to Neo4j Aura...")
    graph.add_graph_documents(all_graph_documents, include_source=True)
    print("Success! All data has been successfully stored in Neo4j Aura.")
    
    return graph

def run_neo4j_rag_chatbot():
    # Option: If you already ran the loader and stored everything, 
    # you can comment out build_and_store_neo4j_graph() and just instantiate Neo4jGraph() directly.
    graph = build_and_store_neo4j_graph()
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Create the Graph Cypher QA Chain
    qa_chain = GraphCypherQAChain.from_llm(
        llm=llm,
        graph=graph,
        verbose=True,  # Shows generated Cypher queries in the terminal
        allow_dangerous_requests=True
    )

    print("\n--- Neo4j Knowledge Graph RAG Chatbot Ready ---")
    print("Ask questions about the full catalog of Tamil Nadu agricultural schemes (type 'exit' to quit).\n")

    while True:
        user_query = input("Ask a question: ").strip()
        if user_query.lower() in ["exit", "quit"]:
            print("Exiting chatbot. Goodbye!")
            break
        
        if not user_query:
            continue

        try:
            print("\nProcessing query through Neo4j Graph...")
            response = qa_chain.invoke({"query": user_query})
            print(f"\nAnswer:\n{response.get('result', response)}\n")
            print("-" * 50)
        except Exception as e:
            print(f"An error occurred while querying the graph: {e}\n")

if __name__ == "__main__":
    run_neo4j_rag_chatbot()