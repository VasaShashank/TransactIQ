import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { Case } from '../types';
import { Briefcase, Plus, Download, Edit3, MessageSquare, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface CaseManagementProps {
  initialAccountId?: string | null;
  onClearInitialAccount?: () => void;
}

export const CaseManagement: React.FC<CaseManagementProps> = ({ initialAccountId, onClearInitialAccount }) => {
  const { user } = useAuth();
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedCase, setSelectedCase] = useState<Case | null>(null);

  // Form State
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [severity, setSeverity] = useState<'low' | 'medium' | 'high' | 'critical'>('high');
  const [relatedAccounts, setRelatedAccounts] = useState<string>('');
  const [newNote, setNewNote] = useState('');
  const [evidenceAccount, setEvidenceAccount] = useState('');
  const [evidenceTransaction, setEvidenceTransaction] = useState('');
  const [evidenceNote, setEvidenceNote] = useState('');

  useEffect(() => {
    fetchCases();
    if (initialAccountId) {
      setRelatedAccounts(initialAccountId);
      setTitle(`Investigation on Target Account ${initialAccountId}`);
      setShowCreateModal(true);
    }
  }, [initialAccountId]);

  const fetchCases = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/cases');
      setCases(res.data.cases);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const accList = relatedAccounts.split(',').map(s => s.trim()).filter(Boolean);
      await apiClient.post('/cases', {
        title,
        description,
        severity,
        related_account_ids: accList
      });
      setShowCreateModal(false);
      setTitle('');
      setDescription('');
      setRelatedAccounts('');
      if (onClearInitialAccount) onClearInitialAccount();
      fetchCases();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error creating case');
    }
  };

  const handleAddNote = async (caseId: number) => {
    if (!newNote.trim()) return;
    try {
      const res = await apiClient.patch<Case>(`/cases/${caseId}`, { new_note: newNote });
      setSelectedCase(res.data);
      setNewNote('');
      fetchCases();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error adding note');
    }
  };

  const handleExportPDF = async (caseId: number) => {
    try {
      const res = await apiClient.get(`/cases/${caseId}/export`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `case_${caseId}_summary.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to export PDF');
    }
  };

  const updateCase = async (caseId: number, payload: Record<string, unknown>) => {
    try {
      const res = await apiClient.patch<Case>(`/cases/${caseId}`, payload);
      setSelectedCase(res.data);
      fetchCases();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Unable to update case');
    }
  };

  const handleAddEvidence = async (caseId: number) => {
    if (!evidenceAccount && !evidenceTransaction) return;
    await updateCase(caseId, {
      evidence: {
        account_id: evidenceAccount || undefined,
        transaction_id: evidenceTransaction ? Number(evidenceTransaction) : undefined,
        note: evidenceNote || undefined
      }
    });
    setEvidenceAccount('');
    setEvidenceTransaction('');
    setEvidenceNote('');
  };

  const handleDeleteCase = async (caseId: number) => {
    if (user?.role !== 'admin' || !window.confirm(`Delete case #${caseId}?`)) return;
    try {
      await apiClient.delete(`/cases/${caseId}`);
      setSelectedCase(null);
      fetchCases();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Unable to delete case');
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Case Management & Investigations</h2>
          <p style={{ color: '#94A3B8', fontSize: '0.9rem' }}>Open, annotate, assign, and export PDF intelligence dossiers</p>
        </div>
        <button onClick={() => setShowCreateModal(true)} className="btn-primary">
          <Plus size={16} /> Open New Investigation Case
        </button>
      </div>

      <div className="glass-card" style={{ overflow: 'hidden' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Case ID</th>
              <th>Title</th>
              <th>Status</th>
              <th>Severity</th>
              <th>Assigned To</th>
              <th>Linked Accounts</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {cases.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ textAlign: 'center', padding: '32px', color: '#64748B' }}>
                  No investigation cases recorded.
                </td>
              </tr>
            ) : (
              cases.map((c) => (
                <tr key={c.id}>
                  <td style={{ fontWeight: 700 }}>#{c.id}</td>
                  <td style={{ fontWeight: 600 }}>{c.title}</td>
                  <td>
                    <span className={`badge ${c.status === 'open' ? 'badge-medium' : c.status === 'closed' ? 'badge-low' : 'badge-high'}`}>
                      {c.status}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${c.severity === 'critical' || c.severity === 'high' ? 'badge-critical' : 'badge-low'}`}>
                      {c.severity}
                    </span>
                  </td>
                  <td style={{ fontSize: '0.85rem', color: '#94A3B8' }}>
                    User #{c.assigned_to || 'Unassigned'}
                  </td>
                  <td>
                    <span className="font-mono" style={{ fontSize: '0.8rem', color: '#60A5FA' }}>
                      {c.related_account_ids.length} Linked
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button onClick={() => setSelectedCase(c)} className="btn-secondary" style={{ padding: '4px 8px', fontSize: '0.75rem' }}>
                        <Edit3 size={14} /> View
                      </button>
                      <button onClick={() => handleExportPDF(c.id)} className="btn-secondary" style={{ padding: '4px 8px', fontSize: '0.75rem' }}>
                        <Download size={14} /> PDF
                      </button>
                      {user?.role === 'admin' && (
                        <button onClick={() => handleDeleteCase(c.id)} className="btn-secondary" style={{ padding: '4px 8px', fontSize: '0.75rem' }} title="Delete case">
                          Delete
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* CREATE CASE MODAL */}
      {showCreateModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 200, padding: '20px' }}>
          <div className="glass-card" style={{ width: '100%', maxWidth: '520px', padding: '28px', background: '#0F172A' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, marginBottom: '16px' }}>Open New Investigation Case</h3>
            <form onSubmit={handleCreateCase} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: '#94A3B8', marginBottom: '4px' }}>Case Title</label>
                <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} className="input-field" style={{ width: '100%' }} required />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: '#94A3B8', marginBottom: '4px' }}>Severity Level</label>
                <select value={severity} onChange={(e: any) => setSeverity(e.target.value)} className="input-field" style={{ width: '100%' }}>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: '#94A3B8', marginBottom: '4px' }}>Related Account IDs (Comma separated)</label>
                <input type="text" value={relatedAccounts} onChange={(e) => setRelatedAccounts(e.target.value)} placeholder="C12345, C67890" className="input-field font-mono" style={{ width: '100%' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: '#94A3B8', marginBottom: '4px' }}>Investigation Summary & Notes</label>
                <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={3} className="input-field" style={{ width: '100%' }} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '10px' }}>
                <button type="button" onClick={() => setShowCreateModal(false)} className="btn-secondary">Cancel</button>
                <button type="submit" className="btn-primary">Create Case</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* VIEW & ANNOTATE CASE MODAL */}
      {selectedCase && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 200, padding: '20px' }}>
          <div className="glass-card" style={{ width: '100%', maxWidth: '640px', padding: '28px', background: '#0F172A', maxHeight: '90vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '16px' }}>
              <div>
                <span className="badge badge-critical">{selectedCase.severity}</span>
                <h3 style={{ fontSize: '1.3rem', fontWeight: 800, marginTop: '4px' }}>{selectedCase.title}</h3>
                <span style={{ fontSize: '0.8rem', color: '#64748B' }}>Case #{selectedCase.id} • Status: {selectedCase.status}</span>
              </div>
              <button onClick={() => setSelectedCase(null)} className="btn-secondary" style={{ padding: '4px 8px' }}>✕</button>
            </div>

            <p style={{ fontSize: '0.9rem', color: '#CBD5E1', marginBottom: '16px' }}>{selectedCase.description || 'No description'}</p>

            <div style={{ marginBottom: '20px' }}>
              <strong style={{ fontSize: '0.85rem', color: '#94A3B8' }}>Linked Accounts:</strong>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '6px' }}>
                {selectedCase.related_account_ids.map(id => (
                  <span key={id} className="badge badge-medium font-mono">{id}</span>
                ))}
              </div>
            </div>

            <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '16px', marginBottom: '16px' }}>
              <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '10px' }}>Evidence</h4>
              {selectedCase.evidence?.map((item, index) => (
                <div key={index} style={{ padding: '8px', marginBottom: '6px', background: 'rgba(15,23,42,0.8)', fontSize: '0.82rem' }}>
                  {item.account_id && <span className="font-mono">Account: {item.account_id} </span>}
                  {item.transaction_id && <span className="font-mono">Transaction: {item.transaction_id} </span>}
                  {item.note && <span>{item.note}</span>}
                </div>
              ))}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                <input className="input-field" placeholder="Account ID" value={evidenceAccount} onChange={(e) => setEvidenceAccount(e.target.value)} />
                <input className="input-field" type="number" placeholder="Transaction ID" value={evidenceTransaction} onChange={(e) => setEvidenceTransaction(e.target.value)} />
                <input className="input-field" placeholder="Evidence note" value={evidenceNote} onChange={(e) => setEvidenceNote(e.target.value)} />
                <button className="btn-secondary" onClick={() => handleAddEvidence(selectedCase.id)}>Attach Evidence</button>
              </div>
            </div>

            <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '16px', marginBottom: '16px' }}>
              <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '10px' }}>Investigation Log & Notes</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '14px' }}>
                {selectedCase.notes.length === 0 ? (
                  <div style={{ fontSize: '0.8rem', color: '#64748B' }}>No notes added yet.</div>
                ) : (
                  selectedCase.notes.map((n, idx) => (
                    <div key={idx} style={{ background: 'rgba(15,23,42,0.8)', padding: '10px', borderRadius: '6px', fontSize: '0.85rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', color: '#64748B', fontSize: '0.75rem', marginBottom: '4px' }}>
                        <span>{n.user_email || `User #${n.user_id}`}</span>
                        <span>{n.timestamp?.slice(0, 19).replace('T', ' ')}</span>
                      </div>
                      <div>{n.note}</div>
                    </div>
                  ))
                )}
              </div>

              <div style={{ display: 'flex', gap: '8px' }}>
                <input
                  type="text"
                  placeholder="Add analyst note..."
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  className="input-field"
                  style={{ flex: 1 }}
                />
                <button onClick={() => handleAddNote(selectedCase.id)} className="btn-primary">
                  <MessageSquare size={16} /> Add Note
                </button>
              </div>
            </div>

            {selectedCase.status !== 'closed' && (
              <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '16px' }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '10px' }}>Closure Review</h4>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <select id="case-verdict" className="input-field" defaultValue="fraud">
                    <option value="fraud">Fraud</option>
                    <option value="false_positive">False positive</option>
                  </select>
                  <button className="btn-primary" onClick={() => {
                    const verdict = (document.getElementById('case-verdict') as HTMLSelectElement).value;
                    updateCase(selectedCase.id, { status: 'closed', verdict });
                  }} disabled={user?.role === 'analyst'}>
                    Approve Closure
                  </button>
                </div>
                {user?.role === 'analyst' && <small style={{ color: '#94A3B8' }}>Senior analyst approval required.</small>}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
