import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { DEPARTMENTS } from '../constants';
import { DestTag } from '../components/Tags';

export const Settings = () => {
  const [threshold, setThreshold] = useState(70);
  const [saved, setSaved] = useState(70);
  const [categories, setCategories] = useState([]);
  const [model, setModel] = useState({ loaded: true, name: '' });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    api
      .get('/settings')
      .then((res) => {
        setThreshold(res.data.confidence_threshold);
        setSaved(res.data.confidence_threshold);
        setCategories(res.data.categories || []);
        setModel({ loaded: res.data.model_loaded, name: (res.data.model_name || '').split(/[\\/]/).slice(-2).join('/') });
      })
      .catch(() => setMessage({ kind: 'error', text: 'Settings could not be loaded.' }))
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      await api.patch('/settings', { confidence_threshold: Number(threshold) });
      setSaved(Number(threshold));
      setMessage({ kind: 'ok', text: `Saved. New uploads below ${threshold}% confidence now go to manual check.` });
    } catch {
      setMessage({ kind: 'error', text: 'The threshold could not be saved.' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="loading">Loading settings…</div>;
  const t = Number(threshold);

  return (
    <div className="page page-narrow">
      <div className="page-head">
        <div>
          <h1 className="page-title">Settings</h1>
          <p className="page-lede">How sure the model must be before a document is routed without a person.</p>
        </div>
      </div>

      {message && (
        <div className={`notice ${message.kind === 'ok' ? 'notice-ok' : 'notice-error'}`} role={message.kind === 'ok' ? 'status' : 'alert'}>
          <span>{message.text}</span>
        </div>
      )}

      <form className="panel panel-body" onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
        <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap' }}>
          <div>
            <label htmlFor="threshold" className="section-title">Confidence threshold</label>
            <p className="hint">Applies to new uploads. Documents already routed keep their status.</p>
          </div>
          <span className="threshold-readout num" aria-live="polite">{t}%</span>
        </div>

        <div className="threshold-scale" aria-hidden="true">
          <span className="zone-check" style={{ flexBasis: `${t}%` }}>{t >= 15 ? 'Manual check' : ''}</span>
          <span className="zone-auto" style={{ flexBasis: `${100 - t}%` }}>{t <= 85 ? 'Routed by AI' : ''}</span>
        </div>
        <input
          id="threshold"
          className="range"
          type="range"
          min="0"
          max="99"
          step="1"
          value={threshold}
          onChange={(e) => setThreshold(e.target.value)}
        />

        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
          <span className="hint">An invoice scored 82.1% would be</span>
          <DestTag category="FINANCE" confidence={82.1} status={82.1 >= t ? 'AI VERIFIED' : 'HUMAN VERIFICATION REQUIRED'} />
          <span className="hint">{82.1 >= t ? 'routed to Finance.' : 'held for a manual check.'}</span>
        </div>

        <div style={{ display: 'flex', gap: 10 }}>
          <button type="submit" className="btn btn-primary" disabled={saving || t === saved}>
            {saving ? 'Saving…' : 'Save threshold'}
          </button>
          {t !== saved && (
            <button type="button" className="btn" onClick={() => setThreshold(saved)}>Undo</button>
          )}
        </div>
      </form>

      <section className="panel panel-body" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <h2 className="section-title">Classifier</h2>
        {model.loaded ? (
          <p className="muted">Model in use: <strong style={{ color: 'var(--ink)' }}>{model.name}</strong>. Its departments are fixed by training:</p>
        ) : (
          <div className="notice notice-check" role="status">
            <span>No trained model is loaded, so every document goes to manual check. Put a model in <code>models/classifier</code> and restart the backend.</span>
          </div>
        )}
        <div className="cat-tags">
          {categories.map((c) => (
            <span key={c} className="chip">{DEPARTMENTS[c] || c}</span>
          ))}
        </div>
      </section>
    </div>
  );
};
