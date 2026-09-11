from neo4j import Session
from typing import Dict, List, Any

class GraphRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_n_hop_graph(self, account_id: str, hops: int = 1) -> Dict[str, Any]:
        cypher = f"""
        MATCH p = (a:Account {{id: $account_id}})-[r:SENT*1..{hops}]-(b:Account)
        RETURN p
        LIMIT 100
        """
        result = self.session.run(cypher, account_id=account_id)
        
        nodes_map = {}
        edges_map = {}

        # Add target node initially
        nodes_map[account_id] = {
            "id": account_id,
            "label": account_id,
            "node_type": "MERCHANT" if account_id.startswith("M") else "CUSTOMER",
            "is_target": True
        }

        for record in result:
            path = record["p"]
            for node in path.nodes:
                nid = node["id"]
                if nid not in nodes_map:
                    nodes_map[nid] = {
                        "id": nid,
                        "label": nid,
                        "node_type": "MERCHANT" if nid.startswith("M") else "CUSTOMER",
                        "is_target": (nid == account_id)
                    }
            for rel in path.relationships:
                rel_id = f"{rel.start_node['id']}_{rel.end_node['id']}_{rel.get('step', 0)}_{rel.get('amount', 0)}"
                if rel_id not in edges_map:
                    edges_map[rel_id] = {
                        "id": rel_id,
                        "source": rel.start_node["id"],
                        "target": rel.end_node["id"],
                        "amount": float(rel.get("amount", 0.0)),
                        "type": str(rel.get("type", "SENT")),
                        "step": int(rel.get("step", 0)),
                        "is_fraud": int(rel.get("isFraud", 0))
                    }

        nodes = [{"data": data} for data in nodes_map.values()]
        edges = [{"data": data} for data in edges_map.values()]
        return {"account_id": account_id, "hops": hops, "nodes": nodes, "edges": edges}

    def get_fan_analysis(self, account_id: str) -> Dict[str, Any]:
        # Distinct senders (fan-in)
        cypher_in = """
        MATCH (s:Account)-[r:SENT]->(a:Account {id: $account_id})
        RETURN DISTINCT s.id AS sender_id
        """
        senders_res = self.session.run(cypher_in, account_id=account_id)
        senders = [r["sender_id"] for r in senders_res]

        # Distinct receivers (fan-out)
        cypher_out = """
        MATCH (a:Account {id: $account_id})-[r:SENT]->(rec:Account)
        RETURN DISTINCT rec.id AS receiver_id
        """
        receivers_res = self.session.run(cypher_out, account_id=account_id)
        receivers = [r["receiver_id"] for r in receivers_res]

        return {
            "account_id": account_id,
            "fan_in_count": len(senders),
            "fan_out_count": len(receivers),
            "senders": senders,
            "receivers": receivers
        }

    def get_degree_centrality(self, account_id: str) -> Dict[str, Any]:
        cypher = """
        MATCH (a:Account {id: $account_id})
        OPTIONAL MATCH (s:Account)-[:SENT]->(a)
        WITH a, count(DISTINCT s) AS in_degree
        OPTIONAL MATCH (a)-[:SENT]->(r:Account)
        WITH a, in_degree, count(DISTINCT r) AS out_degree
        RETURN in_degree, out_degree, (in_degree + out_degree) AS total_degree
        """
        res = self.session.run(cypher, account_id=account_id).single()
        if not res:
            return {"account_id": account_id, "degree_centrality": 0, "in_degree": 0, "out_degree": 0}
        
        return {
            "account_id": account_id,
            "degree_centrality": res["total_degree"] or 0,
            "in_degree": res["in_degree"] or 0,
            "out_degree": res["out_degree"] or 0
        }
