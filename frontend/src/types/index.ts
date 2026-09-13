export interface User {
  id: number;
  email: string;
  role: 'analyst' | 'senior_analyst' | 'admin';
  created_at: string;
}

export interface Account {
  id: string;
  node_type: string;
  created_at?: string;
}

export interface Transaction {
  id: number;
  step: number;
  type: string;
  amount: number;
  orig_account_id: string;
  dest_account_id: string;
  old_balance_orig: number;
  new_balance_orig: number;
  old_balance_dest: number;
  new_balance_dest: number;
  is_fraud: number;
  is_flagged_fraud: number;
}

export interface GraphNode {
  data: {
    id: string;
    label: string;
    node_type: string;
    is_target?: boolean;
  }
}

export interface GraphEdge {
  data: {
    id: string;
    source: string;
    target: string;
    amount: number;
    type: string;
    step: number;
    is_fraud: number;
  }
}

export interface GraphData {
  account_id: string;
  hops: number;
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface FanAnalysis {
  account_id: string;
  fan_in_count: number;
  fan_out_count: number;
  senders: string[];
  receivers: string[];
}

export interface Centrality {
  account_id: string;
  degree_centrality: number;
  in_degree: number;
  out_degree: number;
}

export interface Community {
  account_id: string;
  members: string[];
  member_count: number;
  method: string;
}

export interface RiskScoreBreakdown {
  known_fraud_flag_score: number;
  txn_frequency_score: number;
  outgoing_volume_score: number;
  num_linked_accounts_score: number;
  graph_centrality_score: number;
}

export interface RiskScore {
  account_id: string;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  breakdown: RiskScoreBreakdown;
  explainable_factors: Record<string, string>;
}

export interface RiskQueueItem {
  account_id: string;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  transaction_count: number;
  fraud_count: number;
  outgoing_volume: number;
  velocity_score: number;
  reason: string;
}

export interface CaseNote {
  user_id: number;
  user_email?: string;
  note: string;
  timestamp: string;
}

export interface Case {
  id: number;
  title: string;
  description?: string;
  status: 'open' | 'in_progress' | 'pending_approval' | 'closed';
  severity: 'low' | 'medium' | 'high' | 'critical';
  assigned_to?: number;
  related_account_ids: string[];
  notes: CaseNote[];
  evidence: CaseEvidence[];
  verdict?: 'fraud' | 'false_positive';
  approved_by?: number;
  approved_at?: string;
  closed_by?: number;
  closed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface CaseEvidence {
  account_id?: string;
  transaction_id?: number;
  note?: string;
  added_by: number;
  added_at: string;
}

export interface AuditLog {
  id: number;
  user_id: number;
  user_email?: string;
  action: string;
  target_type?: string;
  target_id?: string;
  timestamp: string;
  metadata_json?: Record<string, any>;
}

export interface AlertMessage {
  type: string;
  transaction_id?: number;
  account_id?: string;
  amount?: number;
  message: string;
  timestamp: string;
}

export interface TimelineResponse {
  transactions: Transaction[];
  total: number;
}

export interface AccountSearchResult {
  accounts: Account[];
  total: number;
  page: number;
  limit: number;
}
