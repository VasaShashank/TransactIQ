import React, { useState } from 'react';
import apiClient from '../api/client';
import { Account, AccountSearchResult } from '../types';
import { Search, Filter, AlertTriangle, ArrowRight, UserCheck } from 'lucide-react';

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

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);
    try {
      const res = await apiClient.get<AccountSearchResult>('/accounts/search', {
        params: {
          query: query || undefined,
          type: type || undefined,
          is_fraud: isFraudOnly ? 1 : undefined,
          min_amount: minAmount ? parseFloat(minAmount) : undefined,
          limit: 20
        }
      });
      setResults(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
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
                    No accounts found matching search criteria.
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
    </div>
  );
};
