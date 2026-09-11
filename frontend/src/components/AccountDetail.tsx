import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { TimelineResponse, GraphData, RiskScore, FanAnalysis, Centrality } from '../types';
import { GraphViewer } from './GraphViewer';
import { RiskBreakdown } from './RiskBreakdown';
import { ArrowLeft, Clock, Network, AlertTriangle, Users, PlusCircle } from 'lucide-react';

interface AccountDetailProps {
  accountId: string;
  onBack: () => void;
  onSelectAccount: (accId: string) => void;
  onCreateCaseForAccount: (accId: string) => void;
}

export const AccountDetail: React.FC<AccountDetailProps> = ({
  accountId,
  onBack,
  onSelectAccount,
  onCreateCaseForAccount
}) => {
  const [activeTab, setActiveTab] = useState<'timeline' | 'graph' | 'risk' | 'fan'>('timeline');
  const [timeline, setTimeline] = useState<TimelineResponse | null>(null);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [riskData, setRiskData] = useState<RiskScore | null>(null);
  const [fanData, setFanData] = useState<FanAnalysis | null>(null);
  const [centrality, setCentrality] = useState<Centrality | null>(null);
  const [hops, setHops] = useState<number>(1);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, [accountId, hops]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [tlRes, riskRes, fanRes, centRes, graphRes] = await Promise.all([
        apiClient.get<TimelineResponse>(`/accounts/${accountId}/timeline`),
        apiClient.get<RiskScore>(`/accounts/${accountId}/risk-score`),
        apiClient.get<FanAnalysis>(`/accounts/${accountId}/fan-analysis`),
        apiClient.get<Centrality>(`/accounts/${accountId}/centrality`),
        apiClient.get<GraphData>(`/accounts/${accountId}/graph`, { params: { hops } })
      ]);
      setTimeline(tlRes.data);
      setRiskData(riskRes.data);
      setFanData(fanRes.data);
      setCentrality(centRes.data);
      setGraphData(graphRes.data);
    } catch (err) {
      console.error('Error fetching account detail:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <button onClick={onBack} className="btn-secondary" style={{ marginBottom: '16px' }}>
        <ArrowLeft size={16} /> Back to Search Results
      </button>

      {/* Account Header */}
      <div className="glass-card" style={{ padding: '24px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ fontSize: '0.8rem', color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Target Account Workspace
          </div>
          <h2 className="font-mono" style={{ fontSize: '1.8rem', fontWeight: 800, color: '#3B82F6', marginTop: '4px' }}>
            {accountId}
          </h2>
          <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
            <span className={`badge ${accountId.startsWith('M') ? 'badge-low' : 'badge-medium'}`}>
              {accountId.startsWith('M') ? 'MERCHANT NODE' : 'CUSTOMER NODE'}
            </span>
            {riskData && (
              <span className={`badge ${riskData.risk_level === 'CRITICAL' || riskData.risk_level === 'HIGH' ? 'badge-critical' : 'badge-low'}`}>
                {riskData.risk_level} RISK ({riskData.risk_score}/100)
              </span>
            )}
          </div>
        </div>

        <button onClick={() => onCreateCaseForAccount(accountId)} className="btn-primary">
          <PlusCircle size={16} /> Open Case for Account
        </button>
      </div>

      {/* Navigation Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: '12px' }}>
        <button
          onClick={() => setActiveTab('timeline')}
          className={`btn-secondary ${activeTab === 'timeline' ? 'btn-primary' : ''}`}
        >
          <Clock size={16} /> Transaction Timeline
        </button>
        <button
          onClick={() => setActiveTab('graph')}
          className={`btn-secondary ${activeTab === 'graph' ? 'btn-primary' : ''}`}
        >
          <Network size={16} /> Graph Visualization (Neo4j)
        </button>
        <button
          onClick={() => setActiveTab('risk')}
          className={`btn-secondary ${activeTab === 'risk' ? 'btn-primary' : ''}`}
        >
          <AlertTriangle size={16} /> Risk Score Breakdown
        </button>
        <button
          onClick={() => setActiveTab('fan')}
          className={`btn-secondary ${activeTab === 'fan' ? 'btn-primary' : ''}`}
        >
          <Users size={16} /> Fan Analysis & Centrality
        </button>
      </div>

      {/* TAB CONTENT */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '48px', color: '#64748B' }}>Loading account intelligence data...</div>
      ) : (
        <>
          {activeTab === 'timeline' && timeline && (
            <div className="glass-card" style={{ overflow: 'hidden' }}>
              <div style={{ padding: '16px 20px', background: 'rgba(15, 23, 42, 0.9)', display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontWeight: 600 }}>Recorded Transactions ({timeline.total} total)</span>
              </div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Step (Hr)</th>
                    <th>Type</th>
                    <th>Amount</th>
                    <th>Origin Account</th>
                    <th>Destination Account</th>
                    <th>Fraud Status</th>
                  </tr>
                </thead>
                <tbody>
                  {timeline.transactions.map((t) => (
                    <tr key={t.id} style={{ background: t.is_fraud === 1 ? 'rgba(239, 68, 68, 0.08)' : 'transparent' }}>
                      <td>{t.step}</td>
                      <td><span className="badge badge-medium">{t.type}</span></td>
                      <td className="font-mono" style={{ fontWeight: 600 }}>${t.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                      <td className="font-mono">
                        <button onClick={() => onSelectAccount(t.orig_account_id)} style={{ background: 'none', border: 'none', color: t.orig_account_id === accountId ? '#FFF' : '#3B82F6', cursor: 'pointer', textDecoration: 'underline' }}>
                          {t.orig_account_id}
                        </button>
                      </td>
                      <td className="font-mono">
                        <button onClick={() => onSelectAccount(t.dest_account_id)} style={{ background: 'none', border: 'none', color: t.dest_account_id === accountId ? '#FFF' : '#3B82F6', cursor: 'pointer', textDecoration: 'underline' }}>
                          {t.dest_account_id}
                        </button>
                      </td>
                      <td>
                        {t.is_fraud === 1 ? (
                          <span className="badge badge-critical">CONFIRMED FRAUD</span>
                        ) : (
                          <span className="badge badge-low">NORMAL</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'graph' && graphData && (
            <div className="glass-card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>N-Hop Transaction Relationship Graph</h3>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <label style={{ fontSize: '0.8rem', color: '#94A3B8' }}>Hops Depth:</label>
                  <select value={hops} onChange={(e) => setHops(Number(e.target.value))} className="input-field" style={{ padding: '4px 8px' }}>
                    <option value={1}>1-Hop</option>
                    <option value={2}>2-Hops</option>
                    <option value={3}>3-Hops</option>
                  </select>
                </div>
              </div>
              <GraphViewer data={graphData} onSelectAccount={onSelectAccount} />
            </div>
          )}

          {activeTab === 'risk' && riskData && (
            <RiskBreakdown data={riskData} />
          )}

          {activeTab === 'fan' && fanData && centrality && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
              <div className="glass-card" style={{ padding: '20px' }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '12px' }}>Graph Centrality Metrics</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '12px', borderRadius: '8px' }}>
                    <span style={{ fontSize: '0.8rem', color: '#94A3B8' }}>Degree Centrality</span>
                    <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#3B82F6' }}>{centrality.degree_centrality}</div>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                    <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '12px', borderRadius: '8px' }}>
                      <span style={{ fontSize: '0.8rem', color: '#94A3B8' }}>Fan-In (In-Degree)</span>
                      <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#10B981' }}>{centrality.in_degree}</div>
                    </div>
                    <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '12px', borderRadius: '8px' }}>
                      <span style={{ fontSize: '0.8rem', color: '#94A3B8' }}>Fan-Out (Out-Degree)</span>
                      <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#F59E0B' }}>{centrality.out_degree}</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="glass-card" style={{ padding: '20px' }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '12px' }}>Connected Senders (Fan-In)</h3>
                <div style={{ maxHeight: '240px', overflowY: 'auto' }}>
                  {fanData.senders.map((s) => (
                    <div key={s} onClick={() => onSelectAccount(s)} className="font-mono" style={{ padding: '8px', cursor: 'pointer', borderBottom: '1px solid rgba(255,255,255,0.05)', color: '#3B82F6', fontSize: '0.85rem' }}>
                      {s}
                    </div>
                  ))}
                </div>
              </div>

              <div className="glass-card" style={{ padding: '20px' }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '12px' }}>Connected Receivers (Fan-Out)</h3>
                <div style={{ maxHeight: '240px', overflowY: 'auto' }}>
                  {fanData.receivers.map((r) => (
                    <div key={r} onClick={() => onSelectAccount(r)} className="font-mono" style={{ padding: '8px', cursor: 'pointer', borderBottom: '1px solid rgba(255,255,255,0.05)', color: '#F59E0B', fontSize: '0.85rem' }}>
                      {r}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
