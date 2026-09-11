from pydantic import BaseModel
from typing import List, Dict, Any

class CytoscapeNodeData(BaseModel):
    id: str
    label: str
    node_type: str
    is_target: bool = False

class CytoscapeNode(BaseModel):
    data: CytoscapeNodeData

class CytoscapeEdgeData(BaseModel):
    id: str
    source: str
    target: str
    amount: float
    type: str
    step: int
    is_fraud: int

class CytoscapeEdge(BaseModel):
    data: CytoscapeEdgeData

class GraphResponse(BaseModel):
    account_id: str
    hops: int
    nodes: List[CytoscapeNode]
    edges: List[CytoscapeEdge]

class FanAnalysisResponse(BaseModel):
    account_id: str
    fan_in_count: int
    fan_out_count: int
    senders: List[str]
    receivers: List[str]

class CentralityResponse(BaseModel):
    account_id: str
    degree_centrality: int
    in_degree: int
    out_degree: int
