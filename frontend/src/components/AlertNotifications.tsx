import React, { useEffect, useState } from 'react';
import { AlertMessage } from '../types';
import { ShieldAlert, X } from 'lucide-react';

export const AlertNotifications: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertMessage[]>([]);

  useEffect(() => {
    // Establish WebSocket connection to backend
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/alerts`;
    
    let ws: WebSocket | null = null;
    try {
      ws = new WebSocket(wsUrl);
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setAlerts((prev) => [data, ...prev.slice(0, 4)]);
        } catch (e) {
          console.error('Failed to parse WS alert data:', e);
        }
      };
    } catch (err) {
      console.warn('WebSocket connection unavailable:', err);
    }

    return () => {
      if (ws) ws.close();
    };
  }, []);

  const removeAlert = (idx: number) => {
    setAlerts((prev) => prev.filter((_, i) => i !== idx));
  };

  if (alerts.length === 0) return null;

  return (
    <div style={{
      position: 'fixed',
      bottom: '24px',
      right: '24px',
      zIndex: 300,
      display: 'flex',
      flexDirection: 'column',
      gap: '10px',
      maxWidth: '380px',
      width: '100%'
    }}>
      {alerts.map((alert, idx) => (
        <div key={idx} className="glass-card animate-fade-in" style={{
          padding: '14px 16px',
          background: 'rgba(239, 68, 68, 0.95)',
          color: '#FFF',
          borderRadius: '10px',
          boxShadow: '0 8px 30px rgba(239, 68, 68, 0.5)',
          display: 'flex',
          alignItems: 'start',
          gap: '12px'
        }}>
          <ShieldAlert size={22} style={{ shrink: 0, marginTop: '2px' }} />
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, fontSize: '0.85rem' }}>REAL-TIME FRAUD TRANSACTION ALERT</div>
            <div style={{ fontSize: '0.8rem', opacity: 0.9, marginTop: '2px' }}>{alert.message}</div>
            {alert.account_id && (
              <div style={{ fontSize: '0.75rem', fontFamily: 'monospace', marginTop: '4px', background: 'rgba(0,0,0,0.2)', padding: '2px 6px', borderRadius: '4px', display: 'inline-block' }}>
                Account: {alert.account_id}
              </div>
            )}
          </div>
          <button onClick={() => removeAlert(idx)} style={{ background: 'none', border: 'none', color: '#FFF', cursor: 'pointer', opacity: 0.8 }}>
            <X size={16} />
          </button>
        </div>
      ))}
    </div>
  );
};
