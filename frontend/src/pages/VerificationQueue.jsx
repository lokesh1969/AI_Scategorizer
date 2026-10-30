import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, CheckCircle2 } from 'lucide-react';
import api from '../services/api';
import { DEPARTMENTS } from '../constants';
import { DestTag, PriorityChip } from '../components/Tags';

export const VerificationQueue = () => {
  const [documents, setDocuments] = useState([]);
  const [threshold, setThreshold] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api
      .get('/verification')
      .then((res) => setDocuments(res.data))
      .catch(() => setError('The queue could not be loaded. Check that the backend is running, then refresh.'))
      .finally(() => setLoading(false));
    api
      .get('/settings')
      .then((res) => setThreshold(res.data.confidence_threshold))
      .catch(() => {});
  }, []);

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1 className="page-title">Manual check</h1>
          <p className="page-lede">
            Documents the model was not sure about{threshold !== null ? ` (below ${threshold}% confidence)` : ''}, plus
            empty or unreadable ones. Open one, decide where it belongs, and it is routed straight away.
          </p>
        </div>
      </div>

      {error && <div className="notice notice-error" role="alert">{error}</div>}

      <div className="panel">
        {loading ? (
          <div className="loading">Loading the queue…</div>
        ) : documents.length === 0 ? (
          <div className="empty">
            <CheckCircle2 size={40} aria-hidden="true" style={{ color: 'var(--ok)', margin: '0 auto' }} />
            <h3>Nothing waiting</h3>
            <p>Every document has been routed or checked.</p>
          </div>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th scope="col">Tag</th>
                  <th scope="col">Document</th>
                  <th scope="col">Model&rsquo;s guess</th>
                  <th scope="col">Priority</th>
                  <th scope="col">Language</th>
                  <th scope="col"><span className="visually-hidden">Action</span></th>
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
                      <div className="cell-sub">Uploaded by {doc.uploader_name}</div>
                    </td>
                    <td className="muted">{DEPARTMENTS[doc.classification?.predicted_category] || 'No guess (unreadable)'}</td>
                    <td><PriorityChip level={doc.priority?.level} /></td>
                    <td className="muted">{doc.language}</td>
                    <td style={{ textAlign: 'right' }}>
                      <Link to={`/documents/${doc._id}`} className="btn btn-check btn-sm">
                        Check it <ArrowRight size={16} aria-hidden="true" />
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
