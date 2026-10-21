import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { CATEGORIES } from '../constants';
import { useAuth } from '../context/AuthContext';
import { Search, Filter, Eye, Trash2, Shield, CheckCircle2, AlertTriangle } from 'lucide-react';

export const Documents = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [languageFilter, setLanguageFilter] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    fetchDocuments();
  }, [categoryFilter, priorityFilter, statusFilter, languageFilter]);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const params = {};
      if (categoryFilter) params.category = categoryFilter;
      if (priorityFilter) params.priority = priorityFilter;
      if (statusFilter) params.status_filter = statusFilter;
      if (languageFilter) params.language = languageFilter;
      if (search) params.search = search;

      const res = await api.get('/documents', { params });
      setDocuments(res.data);
    } catch (err) {
      console.error('Failed to fetch documents', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchDocuments();
  };

  const handleDelete = async (docId, filename) => {
    if (!window.confirm(`Are you sure you want to delete document "${filename}"?`)) return;
    try {
      await api.delete(`/documents/${docId}`);
      setDocuments(documents.filter((d) => d._id !== docId));
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete document');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc' }}>
            Enterprise Document Registry
          </h1>
          <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '4px' }}>
            Showing {documents.length} classified & routed document records.
          </p>
        </div>
      </div>

      {/* Search & Filters Bar */}
      <div className="glass-panel" style={{ padding: '16px 20px', display: 'flex', flexWrap: 'wrap', gap: '12px', alignItems: 'center' }}>
        <form onSubmit={handleSearchSubmit} style={{ flex: 1, minWidth: '240px', position: 'relative' }}>
          <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
          <input
            type="text"
            placeholder="Search document name or content..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px 8px 38px',
              background: 'rgba(15, 23, 42, 0.8)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '6px',
              color: '#f8fafc',
              fontSize: '0.85rem',
              outline: 'none'
            }}
          />
        </form>

        {/* Category Filter */}
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          style={{
            padding: '8px 12px',
            background: 'rgba(15, 23, 42, 0.8)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '6px',
            color: '#f8fafc',
            fontSize: '0.85rem',
            outline: 'none'
          }}
        >
          <option value="">All Categories</option>
          {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
          <option value="UNCLASSIFIED">UNCLASSIFIED</option>
        </select>

        {/* Priority Filter */}
        <select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
          style={{
            padding: '8px 12px',
            background: 'rgba(15, 23, 42, 0.8)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '6px',
            color: '#f8fafc',
            fontSize: '0.85rem',
            outline: 'none'
          }}
        >
          <option value="">All Priorities</option>
          <option value="CRITICAL">CRITICAL</option>
          <option value="HIGH">HIGH</option>
          <option value="MEDIUM">MEDIUM</option>
          <option value="LOW">LOW</option>
        </select>

        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{
            padding: '8px 12px',
            background: 'rgba(15, 23, 42, 0.8)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '6px',
            color: '#f8fafc',
            fontSize: '0.85rem',
            outline: 'none'
          }}
        >
          <option value="">All Statuses</option>
          <option value="AI VERIFIED">AI VERIFIED</option>
          <option value="HUMAN VERIFICATION REQUIRED">HUMAN VERIFICATION REQUIRED</option>
          <option value="HUMAN VERIFIED">HUMAN VERIFIED</option>
        </select>

        {/* Language Filter */}
        <select
          value={languageFilter}
          onChange={(e) => setLanguageFilter(e.target.value)}
          style={{
            padding: '8px 12px',
            background: 'rgba(15, 23, 42, 0.8)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '6px',
            color: '#f8fafc',
            fontSize: '0.85rem',
            outline: 'none'
          }}
        >
          <option value="">All Languages</option>
          <option value="English">English</option>
          <option value="Hindi">Hindi</option>
          <option value="Mixed (Hindi + English)">Mixed</option>
        </select>
      </div>

      {/* Documents Table */}
      <div className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: '40px', textAlignment: 'center', color: '#94a3b8' }}>
            Fetching document records...
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
              <thead>
                <tr style={{ background: 'rgba(15, 23, 42, 0.9)', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase' }}>
                  <th style={{ padding: '14px 20px' }}>Document Name</th>
                  <th style={{ padding: '14px 20px' }}>AI Classification</th>
                  <th style={{ padding: '14px 20px' }}>Confidence</th>
                  <th style={{ padding: '14px 20px' }}>Priority</th>
                  <th style={{ padding: '14px 20px' }}>Status</th>
                  <th style={{ padding: '14px 20px' }}>Routed Department</th>
                  <th style={{ padding: '14px 20px' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {documents.length === 0 ? (
                  <tr>
                    <td colSpan="7" style={{ padding: '40px', textAlign: 'center', color: '#64748b' }}>
                      No document records found matching your filters.
                    </td>
                  </tr>
                ) : (
                  documents.map((doc) => (
                    <tr key={doc._id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)', transition: 'background 0.15s' }}>
                      <td style={{ padding: '14px 20px', fontWeight: 500, color: '#f8fafc' }}>
                        {doc.original_filename}
                        <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>
                          Uploaded by {doc.uploader_name} • {doc.language}
                        </div>
                      </td>
                      <td style={{ padding: '14px 20px' }}>
                        <span className={`badge cat-${doc.classification?.predicted_category?.toLowerCase()}`}>
                          {doc.classification?.predicted_category}
                        </span>
                      </td>
                      <td style={{ padding: '14px 20px', fontWeight: 600, color: '#06b6d4' }}>
                        {doc.classification?.confidence}%
                      </td>
                      <td style={{ padding: '14px 20px' }}>
                        <span className={`badge badge-${doc.priority?.level?.toLowerCase()}`}>
                          {doc.priority?.level}
                        </span>
                      </td>
                      <td style={{ padding: '14px 20px' }}>
                        <span className={`badge ${doc.verification_status === 'AI VERIFIED' ? 'badge-verified' : 'badge-human-req'}`}>
                          {doc.verification_status}
                        </span>
                      </td>
                      <td style={{ padding: '14px 20px', color: '#cbd5e1', fontSize: '0.8rem' }}>
                        {doc.assigned_department}
                      </td>
                      <td style={{ padding: '14px 20px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          <Link to={`/documents/${doc._id}`} title="View Details" style={{ color: '#06b6d4' }}>
                            <Eye size={18} />
                          </Link>
                          {(user?.role === 'ADMIN' || user?._id === doc.uploader_id) && (
                            <button
                              onClick={() => handleDelete(doc._id, doc.original_filename)}
                              title="Delete Document"
                              style={{ background: 'none', border: 'none', color: '#f43f5e', cursor: 'pointer' }}
                            >
                              <Trash2 size={18} />
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
        )}
      </div>
    </div>
  );
};
