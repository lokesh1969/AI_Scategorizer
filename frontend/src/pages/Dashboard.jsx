import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Upload as UploadIcon } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { CATEGORIES, DEPARTMENTS } from '../constants';
import { DestTag, StatusChip, PriorityChip, DEST_CODES, isManualCheck } from '../components/Tags';

const PRIORITY_ORDER = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

const Bin = ({ code, title, docs, total, manual }) => {
  const share = total > 0 ? Math.round((docs.length / total) * 100) : 0;
  return (
    <section className={`bin bin-${code.toLowerCase()}`} aria-label={`${title}: ${docs.length} documents`}>
      <header className="bin-head">
        <span className="bin-code">{code}</span>
        <span className="bin-title">{title}</span>
      </header>
      <div className="bin-count num">{docs.length}</div>
      <div className="bin-meter" aria-hidden="true">
        <span style={{ width: `${share}%` }} />
      </div>
      <ul className="bin-list">
        {docs.slice(0, 3).map((d) => (
          <li key={d._id}>
            <Link to={`/documents/${d._id}`}>
              <span className="bin-file">{d.original_filename}</span>
              <span className="bin-conf num">
                {d.verification_status === 'HUMAN VERIFIED' ? 'Checked' : `${Number(d.classification?.confidence).toFixed(1)}%`}
              </span>
            </Link>
          </li>
        ))}
        {docs.length === 0 && <li className="bin-empty">{manual ? 'Nothing waiting' : 'Empty'}</li>}
      </ul>
    </section>
  );
};

const MixBar = ({ title, entries, total, classFor, label = (k) => k }) => (
  <div className="panel panel-body mix">
    <h2 className="section-title">{title}</h2>
    <div className="mix-bar" aria-hidden="true">
      {entries.filter(([, n]) => n > 0).map(([k, n]) => (
        <span key={k} className={classFor(k)} style={{ flexGrow: n }} />
      ))}
      {total === 0 && <span className="mix-none" style={{ flexGrow: 1 }} />}
    </div>
    <dl className="mix-legend">
      {entries.map(([k, n]) => (
        <div key={k}>
          <dt><span className={`mix-key ${classFor(k)}`} aria-hidden="true" />{label(k)}</dt>
          <dd className="num">{n}</dd>
        </div>
      ))}
    </dl>
  </div>
);

export const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([api.get('/dashboard/stats'), api.get('/documents')])
      .then(([s, d]) => {
        setStats(s.data);
        setDocs(d.data);
      })
      .catch(() => setError('The dashboard could not be loaded. Check that the backend is running, then refresh.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">Loading the sorting floor…</div>;
  if (error) return <div className="notice notice-error" role="alert">{error}</div>;

  const canUpload = ['ADMIN', 'UPLOADER'].includes(user?.role);
  const waiting = docs.filter((d) => isManualCheck(d.verification_status));
  const routed = docs.filter((d) => !isManualCheck(d.verification_status));
  const byCat = (cat) => routed.filter((d) => d.classification?.predicted_category === cat);
  const critical = stats.priority_counts?.CRITICAL || 0;

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1 className="page-title">Sorting floor</h1>
          <p className="page-lede manifest">
            <strong className="num">{docs.length}</strong> documents in view.{' '}
            <strong className={`num${waiting.length ? ' is-check' : ''}`}>{waiting.length}</strong> waiting for a manual check.{' '}
            Average confidence <strong className="num">{stats.average_confidence}%</strong>.{' '}
            {critical > 0 ? (
              <><strong className="num is-danger">{critical}</strong> marked critical.</>
            ) : (
              'Nothing critical.'
            )}
          </p>
        </div>
        {canUpload && (
          <Link to="/upload" className="btn btn-primary">
            <UploadIcon size={18} aria-hidden="true" />
            Upload a document
          </Link>
        )}
      </div>

      <div className="floor">
        {CATEGORIES.map((cat) => (
          <Bin key={cat} code={DEST_CODES[cat]} title={DEPARTMENTS[cat]} docs={byCat(cat)} total={docs.length} />
        ))}
        <Bin code="CHK" title="Manual check" docs={waiting} total={docs.length} manual />
      </div>

      <div className="split-2">
        <MixBar
          title="Priority"
          total={docs.length}
          entries={PRIORITY_ORDER.map((p) => [p, stats.priority_counts?.[p] || 0])}
          classFor={(k) => `mix-p-${k.toLowerCase()}`}
          label={(k) => k.charAt(0) + k.slice(1).toLowerCase()}
        />
        <MixBar
          title="Language"
          total={docs.length}
          entries={Object.entries(stats.language_counts || {})}
          classFor={(k) => `mix-l-${k.split(' ')[0].toLowerCase()}`}
        />
      </div>

      <div className="panel">
        <div className="panel-head">
          <h2 className="section-title">Latest documents</h2>
          <Link to="/documents" className="link-arrow">
            All documents <ArrowRight size={16} aria-hidden="true" />
          </Link>
        </div>
        {docs.length === 0 ? (
          <div className="empty">
            <h3>No documents yet</h3>
            <p>{canUpload ? 'Upload one to see it sorted.' : 'Documents routed to you will appear here.'}</p>
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
                  <th scope="col">Uploaded</th>
                </tr>
              </thead>
              <tbody>
                {docs.slice(0, 6).map((d) => (
                  <tr key={d._id}>
                    <td>
                      <DestTag category={d.classification?.predicted_category} confidence={d.classification?.confidence} status={d.verification_status} />
                    </td>
                    <td>
                      <Link to={`/documents/${d._id}`} className="row-link cell-strong">{d.original_filename}</Link>
                      <div className="cell-sub">{d.file_type} · {d.language}</div>
                    </td>
                    <td><StatusChip status={d.verification_status} /></td>
                    <td><PriorityChip level={d.priority?.level} /></td>
                    <td className="num cell-sub">{new Date(d.upload_timestamp).toLocaleString()}</td>
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
