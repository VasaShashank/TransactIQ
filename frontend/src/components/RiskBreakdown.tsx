import React from 'react';
import { RiskScore } from '../types';
import { AlertTriangle, Info, CheckCircle, Flame } from 'lucide-react';

interface RiskBreakdownProps {
  data: RiskScore;
}

export const RiskBreakdown: React.FC<RiskBreakdownProps> = ({ data }) => {
  const getBadgeClass = (level: string) => {
    switch (level) {
      case 'CRITICAL': return 'badge-critical';
      case 'HIGH': return 'badge-high';
      case 'MEDIUM': return 'badge-medium';
      default: return 'badge-low';
    }
  };

  const factors = [
    { key: 'known_fraud_flag_score', label: 'Known Fraud / Flagged Txn', weight: '35%', desc: data.explainable_factors.known_fraud },
    { key: 'txn_frequency_score', label: 'Transaction Frequency', weight: '20%', desc: data.explainable_factors.txn_frequency },
    { key: 'outgoing_volume_score', label: 'Outgoing Volume', weight: '15%', desc: data.explainable_factors.outgoing_volume },
    { key: 'num_linked_accounts_score', label: 'Linked Accounts (Fan-In/Out)', weight: '15%', desc: data.explainable_factors.linked_accounts },
    { key: 'graph_centrality_score', label: 'Graph Centrality', weight: '15%', desc: data.explainable_factors.graph_centrality },
  ];

  return (
    <div className="glass-card" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Explainable Risk Assessment</h3>
          <span style={{ fontSize: '0.8rem', color: '#94A3B8' }}>Composite Multi-Signal Risk Score Model</span>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '2.2rem', fontWeight: 800, color: data.risk_score >= 50 ? '#EF4444' : '#10B981' }}>
            {data.risk_score} <span style={{ fontSize: '1rem', color: '#64748B' }}>/ 100</span>
          </div>
          <span className={`badge ${getBadgeClass(data.risk_level)}`}>
            {data.risk_level} RISK
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {factors.map((f) => {
          const val = (data.breakdown as any)[f.key] || 0;
          return (
            <div key={f.key} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '14px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '0.85rem' }}>
                <span style={{ fontWeight: 600, color: '#F8FAFC' }}>
                  {f.label} <span style={{ color: '#64748B', fontWeight: 400 }}>(Weight: {f.weight})</span>
                </span>
                <span style={{ fontWeight: 700, color: val > 50 ? '#F59E0B' : '#60A5FA' }}>
                  {val} / 100
                </span>
              </div>

              {/* Progress Bar */}
              <div style={{ width: '100%', height: '6px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '3px', overflow: 'hidden', marginBottom: '8px' }}>
                <div style={{
                  width: `${val}%`,
                  height: '100%',
                  background: val >= 75 ? '#EF4444' : val >= 40 ? '#F59E0B' : '#3B82F6',
                  transition: 'width 0.4s ease'
                }} />
              </div>

              <div style={{ fontSize: '0.75rem', color: '#94A3B8', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Info size={14} color="#64748B" />
                <span>{f.desc}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
