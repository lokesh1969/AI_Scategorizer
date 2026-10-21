import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { CATEGORY_COLORS } from '../constants';
import { 
  FileText, 
  CheckCircle2, 
  AlertTriangle, 
  Clock, 
  TrendingUp, 
  Shield, 
  Layers, 
  Globe, 
  ArrowRight,
  Eye
} from 'lucide-react';

export const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await api.get('/dashboard/stats');
      setStats(res.data);
    } catch (err) {
      console.error('Failed to fetch dashboard stats', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '40px', color: '#94a3b8' }}>
        Loading AI Scategorizer Command Center Analytics...
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Banner */}
      <div className="glass-panel" style={{ padding: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc' }}>
            System Executive Dashboard
          </h1>
          <p style={{ fontSize: '0.875rem', color: '#94a3b8', marginTop: '4px' }}>
            Real-time bilingual document ingestion, OCR, ML classification, and intelligent routing telemetry.
          </p>
        </div>
        <Link 
          to="/upload" 
          style={{
            padding: '10px 18px',
            background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
            borderRadius: '8px',
            color: '#ffffff',
            fontWeight: 600,
            fontSize: '0.875rem',
            textDecoration: 'none',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            boxShadow: '0 4px 15px rgba(6, 182, 212, 0.3)'
          }}
        >
          Upload New Document
          <ArrowRight size={16} />
        </Link>
      </div>

      {/* Metrics Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>Total Documents</span>
            <FileText size={20} color="#06b6d4" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#f8fafc', marginTop: '8px' }}>
            {stats.total_documents}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#34d399', marginTop: '4px' }}>
            100% Ingested & Processed
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>Human Verification Queue</span>
            <AlertTriangle size={20} color="#f59e0b" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: stats.human_verification_count > 0 ? '#fbbf24' : '#f8fafc', marginTop: '8px' }}>
            {stats.human_verification_count}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '4px' }}>
            {stats.human_verification_rate}% Flagged Low Confidence
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>Avg AI Confidence</span>
            <TrendingUp size={20} color="#10b981" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#f8fafc', marginTop: '8px' }}>
            {stats.average_confidence}%
          </div>
          <div style={{ fontSize: '0.75rem', color: '#60a5fa', marginTop: '4px' }}>
            Calibrated Model Output
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>Critical Priority Docs</span>
            <Shield size={20} color="#f43f5e" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#fb7185', marginTop: '8px' }}>
            {stats.priority_counts?.CRITICAL || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#fb7185', marginTop: '4px' }}>
            Requires Immediate Action
          </div>
        </div>
      </div>

      {/* Analytics Breakdown Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
        {/* Category Distribution */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Layers size={18} color="#06b6d4" />
            Category Distribution
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {Object.entries(stats.category_counts || {}).map(([cat, count]) => {
              const pct = stats.total_documents > 0 ? Math.round((count / stats.total_documents) * 100) : 0;
              const colorMap = CATEGORY_COLORS;
              return (
                <div key={cat}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#cbd5e1', marginBottom: '4px' }}>
                    <span>{cat}</span>
                    <span>{count} docs ({pct}%)</span>
                  </div>
                  <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.06)', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{ width: `${pct}%`, height: '100%', background: colorMap[cat] || '#06b6d4', transition: 'width 0.5s ease-out' }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Priority Breakdown */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertTriangle size={18} color="#f59e0b" />
            Priority Breakdown
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {Object.entries(stats.priority_counts || {}).map(([lvl, count]) => {
              const pct = stats.total_documents > 0 ? Math.round((count / stats.total_documents) * 100) : 0;
              const colorMap = { CRITICAL: '#f43f5e', HIGH: '#f59e0b', MEDIUM: '#3b82f6', LOW: '#94a3b8' };
              return (
                <div key={lvl}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#cbd5e1', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 600, color: colorMap[lvl] }}>{lvl}</span>
                    <span>{count} docs ({pct}%)</span>
                  </div>
                  <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.06)', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{ width: `${pct}%`, height: '100%', background: colorMap[lvl] || '#94a3b8', transition: 'width 0.5s ease-out' }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Language Distribution */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Globe size={18} color="#8b5cf6" />
            Bilingual Language Mix
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {Object.entries(stats.language_counts || {}).map(([lang, count]) => {
              const pct = stats.total_documents > 0 ? Math.round((count / stats.total_documents) * 100) : 0;
              return (
                <div key={lang}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#cbd5e1', marginBottom: '4px' }}>
                    <span>{lang}</span>
                    <span>{count} docs ({pct}%)</span>
                  </div>
                  <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.06)', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{ width: `${pct}%`, height: '100%', background: '#8b5cf6', transition: 'width 0.5s ease-out' }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Recent Documents Table */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc' }}>
            Recent Ingested Documents
          </h2>
          <Link to="/documents" style={{ color: '#06b6d4', fontSize: '0.85rem', textDecoration: 'none', fontWeight: 500 }}>
            View All Documents →
          </Link>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.08)', color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase' }}>
                <th style={{ padding: '12px 16px' }}>Document</th>
                <th style={{ padding: '12px 16px' }}>Category</th>
                <th style={{ padding: '12px 16px' }}>Confidence</th>
                <th style={{ padding: '12px 16px' }}>Priority</th>
                <th style={{ padding: '12px 16px' }}>Status</th>
                <th style={{ padding: '12px 16px' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {stats.recent_documents?.map((doc) => (
                <tr key={doc._id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)', transition: 'background 0.15s' }}>
                  <td style={{ padding: '12px 16px', fontWeight: 500, color: '#f8fafc' }}>
                    {doc.original_filename}
                    <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{doc.file_type} • {doc.language}</div>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <span className={`badge cat-${doc.classification?.predicted_category?.toLowerCase()}`}>
                      {doc.classification?.predicted_category}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px', fontWeight: 600, color: '#06b6d4' }}>
                    {doc.classification?.confidence}%
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <span className={`badge badge-${doc.priority?.level?.toLowerCase()}`}>
                      {doc.priority?.level}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <span className={`badge ${doc.verification_status === 'AI VERIFIED' ? 'badge-verified' : 'badge-human-req'}`}>
                      {doc.verification_status}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <Link to={`/documents/${doc._id}`} style={{ color: '#94a3b8', textDecoration: 'none' }}>
                      <Eye size={18} />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
