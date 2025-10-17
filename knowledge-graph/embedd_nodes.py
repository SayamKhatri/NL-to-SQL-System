import time
import openai
import yaml
import os 
from connect import connect_to_db

CONFIG_PATH = os.path.join('config', 'config.yaml')

with open(CONFIG_PATH, 'r') as f:
    config = yaml.safe_load()

openai.api_key = os.getenv('OPEN_API_KEY')

# Function to get all nodes
def fetch_nodes(tx):
    result = tx.run("""
        MATCH (n)
        RETURN labels(n) AS labels, n.name AS name, n.pk AS pk
    """)
    return [record for record in result]

# Function to create embeddings
def get_embedding(text):
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"  
    )
    return response.data[0].embedding

# Function to update node with embedding 
def update_embedding(tx, node_name, labels, embedding):
    tx.run("""
        MATCH (n {name: $node_name})
        WHERE $label IN labels(n)
        SET n.embedding = $embedding
    """, node_name=node_name, label=labels[0], embedding=embedding)

def main():
    driver = connect_to_db()
    with driver.session(database="neo4j") as session:
        nodes = session.execute_read(fetch_nodes)
        
        for node in nodes:
            labels = node['labels']
            name = node['name']
            pk = node['pk']
            
            # Build text to embed
            if 'Database' in labels:
                text_to_embed = f"Database: {name}"
            elif 'Table' in labels:
                text_to_embed = f"Table: {name}"
            elif 'Column' in labels:
                text_to_embed = f"Column: {name}"
                if pk:
                    text_to_embed += " (Primary Key)"
            else:
                continue
            
            # Generate embedding
            embedding = get_embedding(text_to_embed)
            
            # Store embedding in Neo4j
            session.execute_write(update_embedding, name, labels, embedding)
            
            # Throttle to avoid rate limits
            time.sleep(0.1)

    print("All nodes embedded successfully!")


if __name__ == '__main__':
    main()