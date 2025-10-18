from neo4j import GraphDatabase
import numpy as np
import openai
import os 
from dotenv import load_dotenv

# Function to create embeddings
def get_embedding(text):
    load_dotenv()
    openai.api_key = os.getenv('OPENAI_API_KEY')
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"  
    )
    return response.data[0].embedding

def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_context_subgraph(driver, top_nodes, max_depth=2):
    """
    Retrieve a subgraph from Neo4j starting from top-k retrieved nodes.
    
    Args:
        driver: Neo4j driver object
        top_nodes: list of node names retrieved from vector search
        max_depth: maximum BFS depth for traversal
    
    Returns:
        subgraph: dict with node info and relationships
    """
    query = """
    UNWIND $top_nodes AS start_name
    MATCH (n {name: start_name})
    CALL apoc.path.subgraphNodes(n, {
        maxLevel: $max_depth,
        relationshipFilter: "HAS_COLUMN|FOREIGN_KEY|RELATED_TO>"
    })
    YIELD node
    RETURN DISTINCT node.name AS name, labels(node) AS labels
    """
    
    subgraph = {"nodes": [], "edges": []}
    
    with driver.session(database="neo4j") as session:
        results = session.run(query, top_nodes=top_nodes, max_depth=max_depth)
        
        for record in results:
            subgraph["nodes"].append({
                "name": record["name"],
                "labels": record["labels"]
            })
    
    edge_query = """
    UNWIND $node_names AS n1_name
    MATCH (n1 {name: n1_name})-[r]->(n2)
    WHERE n2.name IN $node_names
    RETURN n1.name AS from, type(r) AS rel, n2.name AS to
    """
    
    node_names = [n["name"] for n in subgraph["nodes"]]
    
    with driver.session(database="neo4j") as session:
        results = session.run(edge_query, node_names=node_names)
        for record in results:
            subgraph["edges"].append({
                "from": record["from"],
                "to": record["to"],
                "relationship": record["rel"]
            })
    
    return subgraph

def search_similar_nodes(driver, query, top_k=5):
    # Embed user query
    query_embedding = get_embedding(query)

    # Fetch all nodes with embeddings
    def fetch_all_embeddings(tx):
        result = tx.run("""
            MATCH (n)
            WHERE n.embedding IS NOT NULL
            RETURN labels(n) AS labels, n.name AS name, n.embedding AS embedding
        """)
        return [record for record in result]

    with driver.session(database="neo4j") as session:
        nodes = session.execute_read(fetch_all_embeddings)

    # Compute similarity
    scored = []
    for node in nodes:
        score = cosine_similarity(query_embedding, node["embedding"])
        scored.append((score, node["labels"], node["name"]))

    # Sort and return top_k
    scored.sort(reverse=True, key=lambda x: x[0])
    return scored[:top_k]