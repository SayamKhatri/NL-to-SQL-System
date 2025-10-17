from neo4j import GraphDatabase
import yaml
import os

def connect_to_neo4j():
    CONFIG_PATH = os.path.join('config', 'config.yaml')

    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)

    con_url = config['CON_URL']
    user = config['USER']
    password = config['PASSWORD']

    driver = GraphDatabase.driver(con_url, auth=(user, password))
    with driver.session() as session:
        result = session.run("RETURN 'Connected to Neo4j Aura!' AS msg")
        print(result.single()["msg"])

    return driver
