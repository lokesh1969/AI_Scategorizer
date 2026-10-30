import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, Eye, Trash2, X } from 'lucide-react';
import api from '../services/api';
import { CATEGORIES, DEPARTMENTS } from '../constants';
import { useAuth } from '../context/AuthContext';
import { DestTag, StatusChip, PriorityChip } from '../components/Tags';

export const Documents = () => {
  const { user } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [languageFilter, setLanguageFilter] = useState('');

  const fetchDocuments = async (searchText = search) => {
    setLoading(true);
    setError('');
    try {
      const params = {};
      if (categoryFilter) params.category = categoryFilter;
      if (priorityFilter) params.priority = priorityFilter;
      if (statusFilter) params.status_filter = statusFilter;
      if (languageFilter) params.language = languageFilter;
      if (searchText) params.search = searchText;
      const res = await api.get('/documents', { params });
      setDocuments(res.data);
    } catch {
      setError('Documents could not be loaded. Check that the backend is running, then try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [categoryFilter, priorityFilter, statusFilter, languageFilter]);

  const filtersActive = search || categoryFilter || priorityFilter || statusFilter || languageFilter;
  const clearFilters = () => {
    setSearch('');
    setCategoryFilter('');
    setPriorityFilter('');
    setStatusFilter('');
    setLanguageFilter('');
    if (!categoryFilter && !priorityFilter && !statusFilter && !languageFilter) fetchDocuments('');
  };

  const handleDelete = async (docId, filename) => {
    if (!window.confirm(`Delete "${filename}"? The file and its record are removed permanently.`)) return;
    try {
      await api.delete(`/documents/${docId}`);
      setDocuments((list) => list.filter((d) => d._id !== docId));
    } catch (err) {
      setError(err.response?.data?.detail || 'The document could not be deleted.');
    }
  };

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1 className="page-title">Documents</h1>
          <p className="page-lede">
            {loading ? 'Loading…' : `${documents.length} document${documents.length === 1 ? '' : 's'} you are allowed to see.`}
          </p>
        </div>
      </div>

      <div className="panel toolbar" role="search">
        <form
          className="search input-icon"
          onSubmit={(e) => {
            e.preventDefault();
            fetchDocuments();
          }}
        >
          <Search size={18} aria-hidden="true" />
          <label htmlFor="doc-search" className="visually-hidden">Search documents</label>
          <input
            id="doc-search"
            className="input"
            type="search"
            placeholder="Search by file name or text, then press Enter"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </form>
        <select className="select" aria-label="Department" value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
          <option value="">All departments</option>
          {CATEGORIES.map((c) => <option key={c} value={c}>{DEPARTMENTS[c]}</option>)}
          <option value="UNCLASSIFIED">Unclassified</option>
        </select>
        <select className="select" aria-label="Status" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">All statuses</option>
          <option value="AI VERIFIED">Routed by AI</option>
          <option value="HUMAN VERIFICATION REQUIRED">Manual check</option>
          <option value="HUMAN VERIFIED">Checked by reviewer</option>
        </select>
        <select className="select" aria-label="Priority" value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
          <option value="">All priorities</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
        <select className="select" aria-label="Language" value={languageFilter} onChange={(e) => setLanguageFilter(e.target.value)}>
          <option value="">All languages</option>
          <option value="English">English</option>
          <option value="Hindi">Hindi</option>
          <option value="Mixed (Hindi + English)">Mixed</option>
        </select>
        {filtersActive && (
          <button type="button" className="btn btn-ghost btn-sm" onClick={clearFilters}>
            <X size={16} aria-hidden="true" /> Clear
          </button>
        )}
      </div>

      {error && <div className="notice notice-error" role="alert">{error}</div>}

      <div className="panel">
        {loading ? (
          <div className="loading">Loading documents…</div>
        ) : documents.length === 0 ? (
          <div className="empty">
            <h3>{filtersActive ? 'Nothing matches these filters' : 'No documents yet'}</h3>
            <p>{filtersActive ? 'Clear a filter or try a different search.' : 'Uploaded documents will appear here.'}</p>
          </div>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th scope="col">Tag</th>
                  <th scope="col">Document</th>
                  <th scope="col">Status</th>
                  <th scope="col">Priority</th>
                  <th scope="col">Sent to</th>
                  <th scope="col"><span className="visually-hidden">Actions</span></th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => (
                  <tr key={doc._id}>
                    <td>
                      <DestTag category={doc.classification?.predicted_category} confidence={doc.classification?.confidence} status={doc.verification_status} />
                    </td>
                    <td>
                      <Link to={`/documents/${doc._id}`} className="row-link cell-strong">{doc.original_filename}</Link>
                      <div className="cell-sub">{doc.uploader_name} · {doc.language}</div>
                    </td>
                    <td><StatusChip status={doc.verification_status} /></td>
                    <td><PriorityChip level={doc.priority?.level} /></td>
                    <td className="muted">{doc.assigned_department}</td>
                    <td>
                      <div style={{ display: 'flex', gap: 4, justifyContent: 'flex-end' }}>
                        <Link to={`/documents/${doc._id}`} className="icon-btn" aria-label={`Open ${doc.original_filename}`}>
                          <Eye size={18} />
                        </Link>
                        {(user?.role === 'ADMIN' || user?.id === doc.uploader_id || user?._id === doc.uploader_id) && (
                          <button
                            type="button"
                            className="icon-btn danger"
                            onClick={() => handleDelete(doc._id, doc.original_filename)}
                            aria-label={`Delete ${doc.original_filename}`}
                          >
                            <Trash2 size={18} />
                          </button>
                        )}
                      </div>
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
