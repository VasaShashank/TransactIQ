import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { AccountSearchResult, RiskQueueItem } from '../types';
import { Search, ArrowRight } from 'lucide-react';

interface AccountSearchProps {
  onSelectAccount: (accountId: string) => void;
}

export const AccountSearch: React.FC<AccountSearchProps> = ({ onSelectAccount }) => {
  const [query, setQuery] = useState('');
  const [type, setType] = useState('');
  const [isFraudOnly, setIsFraudOnly] = useState(false);
  const [minAmount, setMinAmount] = useState('');
  const [results, setResults] = useState<AccountSearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [riskQueue, setRiskQueue] = useState<RiskQueueItem[]>([]);

  useEffect(() => {
    apiClient.get<{ items: RiskQueueItem[] }>('/accounts/risk-queue', { params: { limit: 8 } })
      .then((res) => setRiskQueue(res.data.items))
      .catch(() => setRiskQueue([]));
  }, []);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);
    setSearchError(null);
    try {
      const res = await apiClient.get<AccountSearchResult>('/accounts/search', {
        params: {
          query: query || undefined,
          type: type || undefined,
          is_fraud: isFraudOnly ? 1 : undefined,
          min_amount: minAmount ? Number.parseFloat(minAmount) : undefined,
          limit: 20
        }
      });
      setResults(res.data);
    } catch (err) {
      console.error(err);
      setSearchError('Search could not be completed. Check that the API is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'end', marginBottom: '12px' }}>
          <div>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Suspicious Account Queue</h2>
            <p style={{ color: '#94A3B8', fontSize: '0.9rem', marginTop: '4px' }}>Ranked by fraud signals, transaction velocity, and outgoing volume</p>
          </div>
          <span className="badge badge-critical">LIVE RISK VIEW</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
          {riskQueue.map((item) => (
            <button key={item.account_id} onClick={() => onSelectAccount(item.account_id)} className="glass-card" style={{ textAlign: 'left', padding: '16px', cursor: 'pointer', border: '1px solid rgba(239,68,68,0.25)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className="font-mono" style={{ color: '#60A5FA', fontWeight: 700 }}>{item.account_id}</span>
                <span className={`badge ${item.risk_level === 'CRITICAL' || item.risk_level === 'HIGH' ? 'badge-critical' : 'badge-medium'}`}>{item.risk_level}</span>
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, marginTop: '10px' }}>{item.risk_score}<small style={{ fontSize: '0.7rem', color: '#94A3B8' }}>/100</small></div>
              <div style={{ color: '#CBD5E1', fontSize: '0.78rem', marginTop: '6px' }}>{item.reason}</div>
            </button>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Account & Transaction Intelligence Search</h2>
        <p style={{ color: '#94A3B8', fontSize: '0.9rem', marginTop: '4px' }}>
          Filter accounts across PostgreSQL transaction logs and query historical activity
        </p>
      </div>

      <div className="glass-card" style={{ padding: '20px', marginBottom: '24px' }}>
        <form onSubmit={handleSearch} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px', alignItems: 'end' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', color: '#94A3B8', marginBottom: '6px' }}>Account ID</label>
            <input
              type="text"
              placeholder="e.g. C123456789 or M98765"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="input-field font-mono"
              style={{ width: '100%' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', color: '#94A3B8', marginBottom: '6px' }}>Account Type</label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="input-field"
              style={{ width: '100%' }}
            >
              <option value="">All Node Types</option>
              <option value="CUSTOMER">Customer (C)</option>
              <option value="MERCHANT">Merchant (M)</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', color: '#94A3B8', marginBottom: '6px' }}>Min Transaction Amount ($)</label>
            <input
              type="number"
              placeholder="0.00"
              value={minAmount}
              onChange={(e) => setMinAmount(e.target.value)}
              className="input-field"
              style={{ width: '100%' }}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', paddingBottom: '10px' }}>
            <input
              type="checkbox"
              id="fraudOnly"
              checked={isFraudOnly}
              onChange={(e) => setIsFraudOnly(e.target.checked)}
              style={{ accentColor: '#EF4444', width: '16px', height: '16px' }}
            />
            <label htmlFor="fraudOnly" style={{ fontSize: '0.85rem', color: '#F87171', cursor: 'pointer', fontWeight: 600 }}>
              Confirmed Fraud Txns Only
            </label>
          </div>

          {isFraudOnly && (
            <div style={{ gridColumn: '1 / -1', color: '#FCA5A5', background: 'rgba(127, 29, 29, 0.24)', border: '1px solid rgba(248, 113, 113, 0.28)', borderRadius: '8px', padding: '10px 12px', fontSize: '0.82rem' }}>
              Confirmed-fraud mode is active. Results require transactions labeled <span className="font-mono">isFraud = 1</span> in the loaded dataset.
            </div>
          )}

          <div>
            <button type="submit" disabled={loading} className="btn-primary" style={{ width: '100%', justifyContent: 'center' }}>
              <Search size={16} /> {loading ? 'Searching...' : 'Execute Search'}
            </button>
          </div>
        </form>
      </div>

      {results && (
        <div className="glass-card" style={{ overflow: 'hidden' }}>
          <div style={{ padding: '16px 20px', background: 'rgba(15, 23, 42, 0.9)', borderBottom: '1px solid var(--bg-card-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>Matching Accounts ({results.total} total)</span>
            <span style={{ fontSize: '0.8rem', color: '#64748B' }}>Showing Page {results.page}</span>
          </div>

          <table className="data-table">
            <thead>
              <tr>
                <th>Account ID</th>
                <th>Node Type</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {results.accounts.length === 0 ? (
                <tr>
                  <td colSpan={3} style={{ textAlign: 'center', padding: '32px', color: '#64748B' }}>
                    {isFraudOnly
                      ? 'No confirmed fraud transactions are present in the loaded dataset.'
                      : 'No accounts found matching search criteria.'}
                  </td>
                </tr>
              ) : (
                results.accounts.map((acc) => (
                  <tr key={acc.id}>
                    <td className="font-mono" style={{ fontWeight: 700, color: '#3B82F6' }}>
                      {acc.id}
                    </td>
                    <td>
                      <span className={`badge ${acc.node_type === 'MERCHANT' ? 'badge-low' : 'badge-medium'}`}>
                        {acc.node_type}
                      </span>
                    </td>
                    <td>
                      <button
                        onClick={() => onSelectAccount(acc.id)}
                        className="btn-secondary"
                        style={{ padding: '4px 10px', fontSize: '0.8rem' }}
                      >
                        Investigate Account <ArrowRight size={14} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
      {searchError && <div style={{ color: '#F87171', marginTop: '12px' }}>{searchError}</div>}
    </div>
  );
};
