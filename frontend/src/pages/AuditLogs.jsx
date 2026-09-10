import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { History, Shield, Clock } from 'lucide-react';

export const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      const res = await api.get('/audit-logs');
      setLogs(res.data);
    } catch (err) {
      console.error('Failed to fetch audit logs', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <History size={24} color="#06b6d4" />
          Security & Operational Audit Logs
        </h1>
        <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '4px' }}>
          Immutable log trail recording document uploads, verifications, system access, and setting modifications.
        </p>
      </div>

      <div className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: '40px', color: '#94a3b8' }}>Loading audit logs...</div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ background: 'rgba(15, 23, 42, 0.9)', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase' }}>
                  <th style={{ padding: '14px 20px' }}>Timestamp</th>
                  <th style={{ padding: '14px 20px' }}>User Email</th>
                  <th style={{ padding: '14px 20px' }}>Action Triggered</th>
                  <th style={{ padding: '14px 20px' }}>Document / Target ID</th>
                  <th style={{ padding: '14px 20px' }}>Audit Details</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log._id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                    <td style={{ padding: '14px 20px', color: '#94a3b8', whiteSpace: 'nowrap' }}>
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td style={{ padding: '14px 20px', fontWeight: 600, color: '#f8fafc' }}>
                      {log.user_email}
                    </td>
                    <td style={{ padding: '14px 20px' }}>
                      <span className="badge badge-verified" style={{ fontSize: '0.7rem' }}>
                        {log.action}
                      </span>
                    </td>
                    <td style={{ padding: '14px 20px', color: '#06b6d4', fontFamily: 'JetBrains Mono, monospace', fontSize: '0.8rem' }}>
                      {log.document_id || 'N/A'}
                    </td>
                    <td style={{ padding: '14px 20px', color: '#cbd5e1', fontSize: '0.8rem' }}>
                      {log.details ? JSON.stringify(log.details) : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
