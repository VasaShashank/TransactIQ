import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Search, Briefcase, ShieldAlert, LogOut, UserCheck } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const { user, logout } = useAuth();

  return (
    <nav style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '14px 24px',
      background: 'rgba(15, 23, 42, 0.85)',
      backdropFilter: 'blur(16px)',
      borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '8px',
          background: 'linear-gradient(135deg, #3B82F6 0%, #06B6D4 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 12px rgba(59, 130, 246, 0.4)'
        }}>
          <ShieldAlert size={20} color="#FFF" />
        </div>
        <div>
          <h1 style={{ fontSize: '1.1rem', fontWeight: 700, letterSpacing: '-0.02em', background: 'linear-gradient(135deg, #FFF 0%, #94A3B8 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            PaySim Intelligence
          </h1>
          <span style={{ fontSize: '0.7rem', color: '#64748B', display: 'block', marginTop: '-2px' }}>
            Fraud Investigation Platform
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <button
          onClick={() => setActiveTab('search')}
          className={`btn-secondary ${activeTab === 'search' ? 'btn-primary' : ''}`}
          style={{ padding: '8px 14px', fontSize: '0.85rem' }}
        >
          <Search size={16} /> Account Search
        </button>

        <button
          onClick={() => setActiveTab('cases')}
          className={`btn-secondary ${activeTab === 'cases' ? 'btn-primary' : ''}`}
          style={{ padding: '8px 14px', fontSize: '0.85rem' }}
        >
          <Briefcase size={16} /> Case Management
        </button>

        {user?.role === 'admin' && (
          <button
            onClick={() => setActiveTab('audit')}
            className={`btn-secondary ${activeTab === 'audit' ? 'btn-primary' : ''}`}
            style={{ padding: '8px 14px', fontSize: '0.85rem' }}
          >
            <UserCheck size={16} /> Audit Log (Admin)
          </button>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{user?.email}</div>
          <span className={`badge ${user?.role === 'admin' ? 'badge-critical' : 'badge-medium'}`}>
            {user?.role}
          </span>
        </div>

        <button onClick={logout} className="btn-secondary" style={{ padding: '8px 12px' }} title="Logout">
          <LogOut size={16} />
        </button>
      </div>
    </nav>
  );
};
