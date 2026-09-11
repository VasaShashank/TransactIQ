import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { AuditLog } from '../types';
import { ShieldCheck, Filter, RefreshCw } from 'lucide-react';

export const AuditLogViewer: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [actionFilter, setActionFilter] = useState('');

  useEffect(() => {
    fetchAuditLogs();
  }, [actionFilter]);

  const fetchAuditLogs = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/audit-logs', {
        params: {
          action: actionFilter || undefined,
          limit: 50
        }
      });
      setLogs(res.data.logs);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Platform Audit & Compliance Logs</h2>
          <p style={{ color: '#94A3B8', fontSize: '0.9rem' }}>Administrative trace of every search, case action, and export</p>
        </div>
        <button onClick={fetchAuditLogs} className="btn-secondary">
          <RefreshCw size={16} /> Refresh Logs
        </button>
      </div>

      <div className="glass-card" style={{ padding: '16px', marginBottom: '20px', display: 'flex', gap: '14px', alignItems: 'center' }}>
        <Filter size={18} color="#94A3B8" />
        <span style={{ fontSize: '0.85rem', color: '#94A3B8', fontWeight: 600 }}>Filter by Action:</span>
        <select value={actionFilter} onChange={(e) => setActionFilter(e.target.value)} className="input-field">
          <option value="">All Actions</option>
          <option value="SEARCH">SEARCH</option>
          <option value="CASE_CREATE">CASE_CREATE</option>
          <option value="CASE_UPDATE">CASE_UPDATE</option>
          <option value="CASE_EXPORT">CASE_EXPORT</option>
          <option value="GRAPH_VIEW">GRAPH_VIEW</option>
        </select>
      </div>

      <div className="glass-card" style={{ overflow: 'hidden' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Timestamp (UTC)</th>
              <th>User Email</th>
              <th>Action</th>
              <th>Target Type</th>
              <th>Target ID</th>
              <th>Metadata</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ textAlign: 'center', padding: '32px', color: '#64748B' }}>
                  No audit log entries recorded.
                </td>
              </tr>
            ) : (
              logs.map((log) => (
                <tr key={log.id}>
                  <td style={{ fontWeight: 600 }}>#{log.id}</td>
                  <td style={{ fontSize: '0.8rem', color: '#94A3B8' }}>
                    {log.timestamp ? log.timestamp.slice(0, 19).replace('T', ' ') : ''}
                  </td>
                  <td style={{ fontWeight: 600, color: '#3B82F6' }}>{log.user_email || `User #${log.user_id}`}</td>
                  <td>
                    <span className="badge badge-medium">{log.action}</span>
                  </td>
                  <td>{log.target_type || '-'}</td>
                  <td className="font-mono">{log.target_id || '-'}</td>
                  <td className="font-mono" style={{ fontSize: '0.75rem', color: '#64748B', maxWidth: '240px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {JSON.stringify(log.metadata_json)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
