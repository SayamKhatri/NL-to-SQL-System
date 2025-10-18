from langchain.schema import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from agents.prompts import PRUNING_AGENT_SYSTEM_MESSAGE

def pruning_agent(question, nodes, edges):
    GOOGLE_API_KEY = os.getenv('Gemini_API_KEY')

    llm = ChatGoogleGenerativeAI(
        api_key=GOOGLE_API_KEY,
        model='gemini-2.5-flash',  
        temperature=0
    )

    system_msg = SystemMessage(content = PRUNING_AGENT_SYSTEM_MESSAGE)

    human_msg = HumanMessage(content=f"""
    User question: {question}
    Retrieved nodes: {nodes}
    Retrieved edges: {edges}
    """)

    response = llm.invoke([system_msg, human_msg]) 
    standardized_context = response.content
    
    return standardized_context