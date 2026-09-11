import os
import sys
import time
import pandas as pd
from neo4j import GraphDatabase

# Add backend directory or parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))


# pyrefly: ignore [missing-import]
from app.core.config import settings

def load_paysim_to_neo4j(csv_path: str, batch_size: int = 10000, max_rows: int | None = None):
    if not os.path.exists(csv_path):
        print(f"Error: PaySim CSV not found at {csv_path}")
        return

    print(f"Connecting to Neo4j at {settings.NEO4J_URI}...")
    driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))

    with driver.session() as session:
        # Create unique constraint on Account id
        print("Ensuring constraints on Account nodes...")
        session.run("CREATE CONSTRAINT account_id_unique IF NOT EXISTS FOR (a:Account) REQUIRE a.id IS UNIQUE;")

        print(f"Loading {csv_path} into Neo4j in batches of {batch_size}...")
        start_time = time.time()
        total_loaded = 0

        cypher_batch = """
        UNWIND $batch AS row
        MERGE (orig:Account {id: row.nameOrig})
          ON CREATE SET orig.node_type = CASE WHEN row.nameOrig STARTS WITH 'M' THEN 'MERCHANT' ELSE 'CUSTOMER' END
        MERGE (dest:Account {id: row.nameDest})
          ON CREATE SET dest.node_type = CASE WHEN row.nameDest STARTS WITH 'M' THEN 'MERCHANT' ELSE 'CUSTOMER' END
        CREATE (orig)-[:SENT {
          amount: toFloat(row.amount),
          type: row.type,
          step: toInteger(row.step),
          isFraud: toInteger(row.isFraud)
        }]->(dest)
        """

        for chunk in pd.read_csv(csv_path, chunksize=batch_size):
            chunk_start = time.time()
            records = chunk.to_dict(orient='records')
            session.run(cypher_batch, batch=records)
            total_loaded += len(chunk)
            print(f"Processed batch of {len(chunk)} relationships ({total_loaded} total) in {time.time() - chunk_start:.2f}s")
            
            if max_rows and total_loaded >= max_rows:
                print(f"Reached max limit of {max_rows} rows.")
                break

    driver.close()
    print(f"Successfully loaded {total_loaded} relationships into Neo4j in {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    csv_file = os.path.join(os.path.dirname(__file__), "..", "paysim.csv")
    max_r = None
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    if len(sys.argv) > 2:
        max_r = int(sys.argv[2])
    load_paysim_to_neo4j(csv_file, max_rows=max_r)
