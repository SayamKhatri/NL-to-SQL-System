import numpy as np
import openai
import os
from knowledge_graph.connect import connect_to_neo4j
from text_to_SQL.context_graph import get_context_subgraph, search_similar_nodes
from agents.pruning_agent import pruning_agent
from agents.generation_agent import generation_agent
from text_to_SQL.utilities import gen_query_result
import warnings
warnings.filterwarnings('ignore')

def generate_chatdb(question):
    driver = connect_to_neo4j()
    results = search_similar_nodes(driver=driver, query=question)
    top_nodes = set()

    for score, labels, name in results:
        top_nodes.add(name)
    top_nodes = list(top_nodes)

    subgraph = get_context_subgraph(driver, top_nodes, max_depth=2)
    nodes, edges = [], []

    for n in subgraph["nodes"]:
        nodes.append(n)

    for e in subgraph["edges"]:
        edges.append(e)


    standardized_context = pruning_agent(question, nodes, edges)
    gen_query = generation_agent(question, standardized_context)

    print(gen_query_result(gen_query))

if __name__ == '__main__':
    generate_chatdb("List the names of all distinct medications, ordered in an alphabetical order.")
