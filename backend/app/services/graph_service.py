import json
from neo4j import Session as Neo4jSession
from redis import Redis
from app.repositories.graph_repository import GraphRepository
from app.schemas.graph import GraphResponse, FanAnalysisResponse, CentralityResponse

class GraphService:
    def __init__(self, neo4j_session: Neo4jSession, redis_client: Redis | None = None):
        self.graph_repo = GraphRepository(neo4j_session)
        self.redis = redis_client

    def get_graph(self, account_id: str, hops: int = 1) -> GraphResponse:
        cache_key = f"graph:{account_id}:hops:{hops}"
        if self.redis:
            try:
                cached = self.redis.get(cache_key)
                if cached:
                    return GraphResponse(**json.loads(cached))
            except Exception:
                pass

        res = self.graph_repo.get_n_hop_graph(account_id, hops=hops)
        graph_resp = GraphResponse(**res)

        if self.redis:
            try:
                self.redis.setex(cache_key, 600, json.dumps(graph_resp.model_dump()))
            except Exception:
                pass

        return graph_resp

    def get_fan_analysis(self, account_id: str) -> FanAnalysisResponse:
        cache_key = f"fan:{account_id}"
        if self.redis:
            try:
                cached = self.redis.get(cache_key)
                if cached:
                    return FanAnalysisResponse(**json.loads(cached))
            except Exception:
                pass

        res = self.graph_repo.get_fan_analysis(account_id)
        fan_resp = FanAnalysisResponse(**res)

        if self.redis:
            try:
                self.redis.setex(cache_key, 600, json.dumps(fan_resp.model_dump()))
            except Exception:
                pass

        return fan_resp

    def get_centrality(self, account_id: str) -> CentralityResponse:
        cache_key = f"centrality:{account_id}"
        if self.redis:
            try:
                cached = self.redis.get(cache_key)
                if cached:
                    return CentralityResponse(**json.loads(cached))
            except Exception:
                pass

        res = self.graph_repo.get_degree_centrality(account_id)
        centrality_resp = CentralityResponse(**res)

        if self.redis:
            try:
                self.redis.setex(cache_key, 600, json.dumps(centrality_resp.model_dump()))
            except Exception:
                pass

        return centrality_resp
