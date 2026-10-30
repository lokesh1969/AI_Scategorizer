import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, CheckCircle2 } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { API_ORIGIN, CATEGORIES, DEPARTMENTS, REVIEWER_ROLES } from '../constants';
import { DestTag, StatusChip, PriorityChip, DEST_CODES, isManualCheck } from '../components/Tags';

const ENTITY_LABELS = {
  MONEY: 'Amount',
  DATE: 'Date',
  EMAIL: 'Email',
  PHONE: 'Phone',
  DOCUMENT_NUMBER: 'Document no.',
  PERSON: 'Person',
  ORGANIZATION: 'Organisation',
};

const Scores = ({ probs, top, threshold }) => {
  const rows = Object.entries(probs || {}).sort((a, b) => b[1] - a[1]);
  return (
    <div className="scorebars" aria-label="Model scores per department">
      <div className="scorebars-threshold" style={{ '--t': threshold / 100 }} aria-hidden="true">
        <span>{threshold}% threshold</span>
      </div>
      {rows.map(([cat, v]) => {
        const code = DEST_CODES[cat] || cat;
        return (
          <div key={cat} className="scorebar">
            <span className="scorebar-code">{code}</span>
            <span className="scorebar-track">
              <span className={`scorebar-fill fill-${code.toLowerCase()} ${cat === top ? 'is-top' : ''}`} style={{ width: `${v}%` }} />
            </span>
            <span className="scorebar-val num">{Number(v).toFixed(1)}%</span>
          </div>
        );
      })}
    </div>
  );
};

export const DocumentDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [doc, setDoc] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [threshold, setThreshold] = useState(70);

  const [verifiedCategory, setVerifiedCategory] = useState('');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [submitted, setSubmitted] = useState('');

  useEffect(() => {
    setLoading(true);
    api
      .get(`/documents/${id}`)
      .then((res) => {
        setDoc(res.data);
        const cat = res.data.classification?.predicted_category;
        setVerifiedCategory(CATEGORIES.includes(cat) ? cat : 'OPERATIONS');
      })
      .catch((err) => setError(err.response?.data?.detail || 'This document could not be loaded.'))
      .finally(() => setLoading(false));
    api
      .get('/settings')
      .then((res) => setThreshold(res.data.confidence_threshold))
      .catch(() => {});
  }, [id]);

  const handleVerify = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setSubmitError('');
    try {
      const res = await api.post(`/verification/verify/${id}`, { verified_category: verifiedCategory, notes });
      setSubmitted(res.data.assigned_department);
      setTimeout(() => navigate('/verification'), 1200);
    } catch (err) {
      setSubmitError(err.response?.data?.detail || 'The decision could not be saved. Try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="loading">Loading the document…</div>;
  if (error) {
    return (
      <div className="page page-narrow">
        <div className="notice notice-error" role="alert">{error}</div>
        <button type="button" className="btn" onClick={() => navigate(-1)}><ArrowLeft size={16} /> Go back</button>
      </div>
    );
  }
  if (!doc) return null;

  const c = doc.classification || {};
  const manual = isManualCheck(doc.verification_status);
  const isReviewer = ['ADMIN', ...REVIEWER_ROLES].includes(user?.role);
  // Department reviewers work the queue; only an administrator can re-label a routed document
  const canDecide = isReviewer && (manual || user?.role === 'ADMIN');
  const changedByReviewer = doc.verification_status === 'HUMAN VERIFIED' && c.model_prediction && c.model_prediction !== c.predicted_category;

  return (
    <div className="page">
      <button type="button" className="btn btn-ghost btn-sm" style={{ alignSelf: 'flex-start' }} onClick={() => navigate(-1)}>
        <ArrowLeft size={16} aria-hidden="true" /> Back
      </button>

      <div className="panel doc-head">
        <DestTag category={c.predicted_category} confidence={c.confidence} status={doc.verification_status} size="lg" barcode />
        <div style={{ minWidth: 0 }}>
          <h1 className="doc-head-title">{doc.original_filename}</h1>
          <div className="doc-facts">
            <span><b>Sent to</b> {doc.assigned_department}</span>
            <span><b>Type</b> {doc.file_type}</span>
            <span><b>Language</b> {doc.language}</span>
            <span><b>Uploaded by</b> {doc.uploader_name}</span>
            <span className="num"><b>On</b> {new Date(doc.upload_timestamp).toLocaleString()}</span>
          </div>
          <div className="doc-chips">
            <StatusChip status={doc.verification_status} />
            <PriorityChip level={doc.priority?.level} />
          </div>
        </div>
      </div>

      {manual && (
        <div className="notice notice-check" role="status">
          <AlertTriangle size={20} aria-hidden="true" />
          <span>
            <strong>Waiting for a manual check.</strong> The model&rsquo;s best guess, {DEPARTMENTS[c.predicted_category] || 'none'}, scored {c.confidence}%, below the {threshold}% threshold, so it was not routed automatically.
          </span>
        </div>
      )}
      {doc.verification_status === 'HUMAN VERIFIED' && (
        <div className="notice" role="status">
          <CheckCircle2 size={20} aria-hidden="true" style={{ color: 'var(--fin)' }} />
          <span>
            Checked by <strong>{doc.verifier_name}</strong>
            {changedByReviewer
              ? `, who re-routed it from ${DEPARTMENTS[c.model_prediction]} (the model's guess) to ${DEPARTMENTS[c.predicted_category]}.`
              : `, who confirmed ${DEPARTMENTS[c.predicted_category]}.`}
            {doc.verification_notes ? ` Note: “${doc.verification_notes}”` : ''}
          </span>
        </div>
      )}

      <div className="doc-grid">
        <div className="doc-col">
          <section className="panel panel-body doc-section">
            <h2 className="section-title">How sure the model was</h2>
            <Scores probs={c.probabilities} top={c.model_prediction || c.predicted_category} threshold={threshold} />
          </section>

          <section className="panel panel-body doc-section">
            <h2 className="section-title">In a few lines</h2>
            <p className="summary-lines">{doc.summary}</p>
          </section>

          <section className="panel panel-body doc-section">
            <h2 className="section-title">What it found</h2>
            {doc.entities?.length ? (
              <div className="entity-list">
                {doc.entities.map((ent, i) => (
                  <span key={i} className="entity">
                    <span className="entity-k">{ENTITY_LABELS[ent.label] || ent.label}</span>
                    <span className="entity-v">{ent.text}</span>
                  </span>
                ))}
              </div>
            ) : (
              <p className="muted">No amounts, dates, numbers or names were found.</p>
            )}
            <dl className="kv">
              <dt>Priority</dt>
              <dd>
                <PriorityChip level={doc.priority?.level} /> <span className="num">{doc.priority?.score}/100</span>
                <div className="hint" style={{ marginTop: 4 }}>{doc.priority?.reason}</div>
              </dd>
              <dt>Tone</dt>
              <dd>{doc.sentiment?.label?.charAt(0)}{doc.sentiment?.label?.slice(1).toLowerCase()} <span className="hint num">({doc.sentiment?.score})</span></dd>
            </dl>
          </section>

          <section className="panel panel-body doc-section">
            <h2 className="section-title">Extracted text</h2>
            <label htmlFor="raw-text" className="visually-hidden">Extracted text</label>
            <textarea id="raw-text" className="raw-text" readOnly value={doc.extracted_text || ''} />
          </section>
        </div>

        <div className="doc-col">
          {canDecide && (
            <section className="panel review-box" aria-labelledby="review-title">
              <div className="panel-head">
                <h2 id="review-title" className="section-title">Your decision</h2>
              </div>
              <form className="panel-body doc-section" onSubmit={handleVerify}>
                {submitted ? (
                  <div className="notice notice-ok" role="status">
                    <CheckCircle2 size={18} aria-hidden="true" />
                    <span>Saved. Sent to <strong>{submitted}</strong>. Returning to the queue…</span>
                  </div>
                ) : (
                  <>
                    {submitError && <div className="notice notice-error" role="alert">{submitError}</div>}
                    <div className="field">
                      <label htmlFor="verify-cat">Send this document to</label>
                      <select id="verify-cat" className="select" value={verifiedCategory} onChange={(e) => setVerifiedCategory(e.target.value)}>
                        {CATEGORIES.map((cat) => (
                          <option key={cat} value={cat}>{DEPARTMENTS[cat]}</option>
                        ))}
                      </select>
                      <span className="hint">
                        {verifiedCategory === (c.model_prediction || c.predicted_category)
                          ? 'Agrees with the model’s guess.'
                          : 'Overrules the model; its guess is kept in the record.'}
                      </span>
                    </div>
                    <div className="field">
                      <label htmlFor="verify-notes">Note for the record (optional)</label>
                      <textarea id="verify-notes" className="textarea" rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Why this department?" />
                    </div>
                    <button type="submit" className="btn btn-primary" disabled={submitting}>
                      {submitting ? 'Saving…' : `Send to ${DEPARTMENTS[verifiedCategory]}`}
                    </button>
                  </>
                )}
              </form>
            </section>
          )}

          <section className="panel panel-body doc-section">
            <h2 className="section-title">How it was read</h2>
            <dl className="kv">
              <dt>Method</dt>
              <dd>{doc.ocr_metadata?.ocr_used ? `OCR (${doc.ocr_metadata.language})` : 'Text read directly from the file'}</dd>
              {doc.ocr_metadata?.error && (
                <>
                  <dt>OCR problem</dt>
                  <dd className="muted">{doc.ocr_metadata.error}</dd>
                </>
              )}
              {c.model_name && (
                <>
                  <dt>Classifier</dt>
                  <dd className="muted" style={{ wordBreak: 'break-word' }}>{c.model_name.split(/[\\/]/).slice(-2).join('/')}</dd>
                </>
              )}
            </dl>
            {doc.ocr_metadata?.preprocessing_applied?.length > 0 && (
              <div className="steps">
                {doc.ocr_metadata.preprocessing_applied.map((s) => (
                  <span key={s} className="step">{s}</span>
                ))}
              </div>
            )}
            {doc.ocr_metadata?.preprocessed_image_url && (
              <figure>
                <img className="preview-img" src={`${API_ORIGIN}${doc.ocr_metadata.preprocessed_image_url}`} alt="The scan after clean-up, as the OCR engine saw it" />
                <figcaption className="hint" style={{ marginTop: 6 }}>The scan after clean-up, as the OCR engine read it.</figcaption>
              </figure>
            )}
          </section>
        </div>
      </div>
    </div>
  );
};
