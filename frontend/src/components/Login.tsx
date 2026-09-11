import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { ShieldAlert, KeyRound, Mail, AlertCircle } from 'lucide-react';

export const Login: React.FC = () => {
  const { login, isLoading } = useAuth();
  const [email, setEmail] = useState('analyst@fraud.intel');
  const [password, setPassword] = useState('analyst123');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await login(email, password);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Please check credentials.');
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div className="glass-card" style={{ width: '100%', maxWidth: '420px', padding: '36px' }}>
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{
            width: '56px',
            height: '56px',
            borderRadius: '14px',
            background: 'linear-gradient(135deg, #3B82F6 0%, #06B6D4 100%)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 8px 24px rgba(59, 130, 246, 0.4)',
            marginBottom: '16px'
          }}>
            <ShieldAlert size={32} color="#FFF" />
          </div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>Analyst Intelligence Portal</h2>
          <p style={{ fontSize: '0.85rem', color: '#94A3B8', marginTop: '6px' }}>
            PaySim Transaction Intelligence & Case Platform
          </p>
        </div>

        {error && (
          <div style={{
            padding: '12px 14px',
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '8px',
            color: '#F87171',
            fontSize: '0.85rem',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '20px'
          }}>
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#94A3B8', marginBottom: '6px' }}>
              Email Address
            </label>
            <div style={{ position: 'relative' }}>
              <Mail size={18} color="#64748B" style={{ position: 'absolute', left: '12px', top: '12px' }} />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-field"
                style={{ width: '100%', paddingLeft: '40px' }}
                required
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#94A3B8', marginBottom: '6px' }}>
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <KeyRound size={18} color="#64748B" style={{ position: 'absolute', left: '12px', top: '12px' }} />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-field"
                style={{ width: '100%', paddingLeft: '40px' }}
                required
              />
            </div>
          </div>

          <div style={{ marginTop: '8px' }}>
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary"
              style={{ width: '100%', justifyContent: 'center', padding: '12px' }}
            >
              {isLoading ? 'Authenticating...' : 'Sign In to Investigation Console'}
            </button>
          </div>
        </form>

        <div style={{ marginTop: '24px', paddingTop: '18px', borderTop: '1px solid rgba(255, 255, 255, 0.08)', fontSize: '0.75rem', color: '#64748B', textAlign: 'center' }}>
          <strong>Default Seed Accounts:</strong><br />
          Analyst: analyst@fraud.intel / analyst123<br />
          Admin: admin@fraud.intel / admin123
        </div>
      </div>
    </div>
  );
};
