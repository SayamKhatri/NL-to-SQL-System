from connect import connect_to_db

def create_hospital_kg(tx, database_name, tables, columns, primary_keys, foreign_keys):

    driver = connect_to_db()
    
    # Database node
    tx.run("MERGE (d:Database {name: $db_name})", db_name=database_name)
    
    # Tables
    for table in tables:
        tx.run("""
            MERGE (t:Table {name: $table})
            WITH t
            MATCH (d:Database {name: $db_name})
            MERGE (d)-[:HAS_TABLE]->(t)
        """, table=table, db_name=database_name)
    
    # Columns
    for col in columns:
        table_name, col_name = col.split('.', 1)
        is_pk = col in primary_keys
        tx.run("""
            MERGE (c:Column {name: $col_name, pk: $is_pk})
            WITH c
            MATCH (t:Table {name: $table_name})
            MERGE (t)-[:HAS_COLUMN]->(c)
        """, col_name=col_name, table_name=table_name, is_pk=is_pk)
    
    # Foreign Keys
    for src, tgt in foreign_keys:
        src_table, src_col = src.split('.', 1)
        tgt_table, tgt_col = tgt.split('.', 1)
        tx.run("""
            MATCH (c1:Column {name: $src_col})<-[:HAS_COLUMN]-(t1:Table {name: $src_table}),
                  (c2:Column {name: $tgt_col})<-[:HAS_COLUMN]-(t2:Table {name: $tgt_table})
            MERGE (c1)-[:FOREIGN_KEY]->(c2)
        """, src_col=src_col, src_table=src_table, tgt_col=tgt_col, tgt_table=tgt_table)


    # Function to update PK flag in Neo4j
    def update_pk(tx, column_name, table_name, is_pk):
        tx.run("""
            MATCH (c:Column {name: $column_name})
            WHERE exists((:Table {name: $table_name})-[:HAS_COLUMN]->(c))
            SET c.pk = $is_pk
        """, column_name=column_name, table_name=table_name, is_pk=is_pk)
            
    with driver.session(database="neo4j") as session:
        session.execute_write(
            create_hospital_kg,
            "hospital_1",
            tables,
            columns,
            primary_keys,
            foreign_keys
        )

    with driver.session(database="neo4j") as session:
        for col, tab in zip(columns, tables):
            full_name = f"{tab}.{col}"
            is_pk = full_name in primary_keys
            session.execute_write(update_pk, col, tab, is_pk)

    driver.close()