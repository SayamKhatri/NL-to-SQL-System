import sqlite3
import pandas as pd 
import os

def connect_db():
    db_path = os.path.join('db', 'hospital_1.sqlite')
    conn = sqlite3.connect(db_path)
    return db_path

def gold_query_result(query):
  conn = connect_db()
  df = pd.read_sql(query, conn)
  df = df.applymap(lambda x: str(x).strip().lower())
  set_gold = set(map(tuple, df.values))
  conn.close()

  return set_gold

def gen_query_result(gen_query):
    conn = connect_db()
    try:
        df = pd.read_sql(gen_query, conn)
    except:
        df = None
        
    df = df.applymap(lambda x: str(x).strip().lower())
    set_gen = set(map(tuple, df.values))
    conn.close()

    return set_gen
