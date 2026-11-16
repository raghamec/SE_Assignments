import os
import certifi
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import networkx as nx

# Fix SSL certificate verification for Windows
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

load_dotenv()

from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer

def build_networkx_graph():
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

    # Load ALL scheme documents instead of a slice [:5]
    all_documents = []
    for i, link in enumerate(scheme_links):
        print(f"[{i+1}/{len(scheme_links)}] Loading: {link}")
        try:
            loader = WebBaseLoader(link)
            docs = loader.load()
            all_documents.extend(docs)
        except Exception as e:
            print(f"  -> Error loading {link}: {e}")

    print(f"\nSuccessfully loaded {len(all_documents)} documents. Extracting entities across all documents (this may take a minute)...")

    # Step 2 & 3: Extract graph entities using LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_transformer = LLMGraphTransformer(llm=llm)
    
    # Process documents in batches or all at once (LLMGraphTransformer handles batches well)
    graph_documents = llm_transformer.convert_to_graph_documents(all_documents)

    # Step 4: Build NetworkX Graph
    print("Building in-memory NetworkX Graph from all extracted data...")
    G = nx.DiGraph()
    for gdoc in graph_documents:
        for node in gdoc.nodes:
            G.add_node(node.id, type=node.type)
        for rel in gdoc.relationships:
            G.add_edge(rel.source.id, rel.target.id, relationship=rel.type)

    print(f"Graph built successfully! Total Nodes: {G.number_of_nodes()}, Total Edges: {G.number_of_edges()}")
    return G

def retrieve_graph_context(query: str, G: nx.DiGraph) -> str:
    """Searches the NetworkX graph for nodes matching the query keywords and extracts their neighborhood."""
    query_terms = query.lower().split()
    relevant_nodes = set()

    # Find nodes whose ID/name matches query keywords
    for node in G.nodes():
        node_lower = str(node).lower()
        if any(term in node_lower for term in query_terms):
            relevant_nodes.add(node)

    # If no direct match, fallback to including sample scheme nodes
    if not relevant_nodes:
        relevant_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'Scheme'][:5]

    # Gather local subgraph context (1-hop neighborhoods)
    context_lines = []
    for node in relevant_nodes:
        node_type = G.nodes[node].get('type', 'Entity')
        context_lines.append(f"Entity: [{node_type}] {node}")
        
        # Outgoing edges
        for successor in G.successors(node):
            rel = G.get_edge_data(node, successor).get('relationship', 'RELATED_TO')
            succ_type = G.nodes[successor].get('type', 'Entity')
            context_lines.append(f"  - ({node}) -[{rel}]-> ([{succ_type}] {successor})")
            
        # Incoming edges
        for predecessor in G.predecessors(node):
            rel = G.get_edge_data(predecessor, node).get('relationship', 'RELATED_TO')
            pred_type = G.nodes[predecessor].get('type', 'Entity')
            context_lines.append(f"  - ([{pred_type}] {predecessor}) -[{rel}]-> ({node})")

    return "\n".join(context_lines) if context_lines else "No direct graph matches found."

def run_networkx_rag_chatbot():
    G = build_networkx_graph()
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    print("\n--- NetworkX Knowledge Graph RAG Chatbot Ready ---")
    print("Ask questions about the full catalog of Tamil Nadu agricultural schemes (type 'exit' to quit).\n")

    while True:
        user_query = input("Ask a question: ").strip()
        if user_query.lower() in ["exit", "quit"]:
            print("Exiting chatbot. Goodbye!")
            break
        
        if not user_query:
            continue

        print("\nRetrieving relevant graph context...")
        graph_context = retrieve_graph_context(user_query, G)

        prompt = f"""
You are an AI assistant answering questions based on a comprehensive Knowledge Graph extracted from Tamil Nadu government agricultural schemes.

Use the following Graph Context (Nodes and Relationships) to answer the user's question accurately. If the answer cannot be found in the context, state that clearly.

Graph Context:
{graph_context}

User Question: {user_query}
Answer:
"""

        print("Generating response...")
        response = llm.invoke(prompt)
        print(f"\nAnswer:\n{response.content}\n")
        print("-" * 50)

if __name__ == "__main__":
    run_networkx_rag_chatbot()