import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

const ACTION_NAMES = {
  LOGIN: 'Signed in',
  UPLOAD: 'Uploaded',
  DOCUMENT_VIEWED: 'Opened document',
  DOCUMENT_DELETED: 'Deleted document',
  HUMAN_VERIFIED: 'Checked document',
  USER_CREATED: 'Added user',
  USER_UPDATED: 'Updated user',
  ROLE_CHANGED: 'Changed role',
  SETTINGS_CHANGED: 'Changed settings',
};

// Turn the stored details object into a short readable line
const describe = (log) => {
  const d = log.details || {};
  switch (log.action) {
    case 'UPLOAD':
      return `${d.filename}: ${d.category} at ${d.confidence}%, ${d.status === 'AI VERIFIED' ? 'routed by AI' : 'held for manual check'}`;
    case 'HUMAN_VERIFIED':
      return d.model_prediction && d.model_prediction !== d.verified_category
        ? `Re-routed from ${d.model_prediction} to ${d.verified_category}`
        : `Confirmed ${d.verified_category}`;
    case 'DOCUMENT_VIEWED':
    case 'DOCUMENT_DELETED':
      return d.filename;
    case 'SETTINGS_CHANGED':
      return `Confidence threshold set to ${d.confidence_threshold}%`;
    case 'USER_CREATED':
      return `${d.created_user_email} as ${d.role}`;
    case 'ROLE_CHANGED':
    case 'USER_UPDATED':
      return `${d.updated_user}: ${Object.entries(d.updates || {}).map(([k, v]) => `${k} → ${v}`).join(', ')}`;
    case 'LOGIN':
      return d.ip ? `From ${d.ip}` : '';
    default:
      return Object.keys(d).length ? JSON.stringify(d) : '';
  }
};

export const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api
      .get('/audit-logs')
      .then((res) => setLogs(res.data))
      .catch(() => setError('The audit log could not be loaded.'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1 className="page-title">Audit log</h1>
          <p className="page-lede">The latest 200 recorded actions: sign-ins, uploads, document views, checks, and changes to users and settings.</p>
        </div>
      </div>

      {error && <div className="notice notice-error" role="alert">{error}</div>}

      <div className="panel">
        {loading ? (
          <div className="loading">Loading the audit log…</div>
        ) : logs.length === 0 ? (
          <div className="empty"><h3>No entries yet</h3></div>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th scope="col">When</th>
                  <th scope="col">Who</th>
                  <th scope="col">Action</th>
                  <th scope="col">Details</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log._id}>
                    <td className="num cell-sub" style={{ whiteSpace: 'nowrap' }}>{new Date(log.timestamp).toLocaleString()}</td>
                    <td className="cell-strong">{log.user_email}</td>
                    <td><span className="audit-action">{ACTION_NAMES[log.action] || log.action}</span></td>
                    <td className="audit-details">
                      {log.document_id && log.action !== 'DOCUMENT_DELETED' ? (
                        <Link to={`/documents/${log.document_id}`} className="row-link">{describe(log) || 'Open document'}</Link>
                      ) : (
                        describe(log) || '—'
                      )}
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
