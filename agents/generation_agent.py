from langchain.schema import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from agents.prompts import GENERATION_AGENT_SYSTEM_MESSAGE

def generation_agent(question, standardized_context):
    GOOGLE_API_KEY = os.getenv('Gemini_API_KEY')

    llm = ChatGoogleGenerativeAI(
        api_key=GOOGLE_API_KEY,
        model='gemini-2.5-flash',  
        temperature=0
    )

    system_msg_sql = SystemMessage(content=GENERATION_AGENT_SYSTEM_MESSAGE)

    human_msg_sql = HumanMessage(content=f"""
    User question: {question}
    Structured context: {standardized_context}
    """)

    sql_response = llm.invoke([system_msg_sql, human_msg_sql])
    sql_query = sql_response.content

    gen_query = sql_query.replace("```sql", "").replace("```", "").strip()
    
    return gen_query