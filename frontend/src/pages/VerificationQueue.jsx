import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { CheckCircle2, AlertTriangle, Eye, ArrowRight, Shield } from 'lucide-react';

export const VerificationQueue = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchQueue();
  }, []);

  const fetchQueue = async () => {
    try {
      const res = await api.get('/verification');
      setDocuments(res.data);
    } catch (err) {
      console.error('Failed to fetch verification queue', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <AlertTriangle color="#f59e0b" size={26} />
          Human Verification Queue
        </h1>
        <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '4px' }}>
          Documents routed here because AI classification confidence is below the configured system threshold (70.0%).
        </p>
      </div>

      <div className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: '40px', textAlignment: 'center', color: '#94a3b8' }}>
            Fetching pending verification queue...
          </div>
        ) : documents.length === 0 ? (
          <div style={{ padding: '48px 24px', textAlign: 'center' }}>
            <CheckCircle2 size={48} color="#10b981" style={{ marginBottom: '12px' }} />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc' }}>
              Verification Queue Empty
            </h3>
            <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '4px' }}>
              All documents have met confidence thresholds or have been manually verified.
            </p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
              <thead>
                <tr style={{ background: 'rgba(15, 23, 42, 0.9)', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase' }}>
                  <th style={{ padding: '14px 20px' }}>Document</th>
                  <th style={{ padding: '14px 20px' }}>AI Predicted Category</th>
                  <th style={{ padding: '14px 20px' }}>Confidence Score</th>
                  <th style={{ padding: '14px 20px' }}>Priority</th>
                  <th style={{ padding: '14px 20px' }}>Language</th>
                  <th style={{ padding: '14px 20px' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => (
                  <tr key={doc._id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                    <td style={{ padding: '14px 20px', fontWeight: 500, color: '#f8fafc' }}>
                      {doc.original_filename}
                      <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>
                        Uploaded by {doc.uploader_name}
                      </div>
                    </td>
                    <td style={{ padding: '14px 20px' }}>
                      <span className={`badge cat-${doc.classification?.predicted_category?.toLowerCase()}`}>
                        {doc.classification?.predicted_category}
                      </span>
                    </td>
                    <td style={{ padding: '14px 20px', fontWeight: 700, color: '#fbbf24' }}>
                      ⚠ {doc.classification?.confidence}%
                    </td>
                    <td style={{ padding: '14px 20px' }}>
                      <span className={`badge badge-${doc.priority?.level?.toLowerCase()}`}>
                        {doc.priority?.level}
                      </span>
                    </td>
                    <td style={{ padding: '14px 20px', color: '#cbd5e1', fontSize: '0.8rem' }}>
                      {doc.language}
                    </td>
                    <td style={{ padding: '14px 20px' }}>
                      <Link 
                        to={`/documents/${doc._id}`} 
                        style={{
                          padding: '6px 14px',
                          background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
                          borderRadius: '6px',
                          color: '#ffffff',
                          fontSize: '0.8rem',
                          fontWeight: 600,
                          textDecoration: 'none',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '6px'
                        }}
                      >
                        Review & Verify
                        <ArrowRight size={14} />
                      </Link>
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
