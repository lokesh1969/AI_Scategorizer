import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Settings as SettingsIcon, Sliders, ShieldCheck } from 'lucide-react';

export const Settings = () => {
  const [confidenceThreshold, setConfidenceThreshold] = useState(70.0);
  const [categories, setCategories] = useState(['FINANCE', 'HR', 'LEGAL', 'OPERATIONS']);
  const [modelName, setModelName] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const res = await api.get('/settings');
      setConfidenceThreshold(res.data.confidence_threshold);
      setCategories(res.data.categories);
      setModelName(res.data.model_loaded ? res.data.model_name : 'No model loaded (all documents go to human review)');
    } catch (err) {
      console.error('Failed to fetch settings', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');
    try {
      await api.patch('/settings', {
        confidence_threshold: parseFloat(confidenceThreshold)
      });
      setMessage('System settings saved successfully!');
    } catch (err) {
      setMessage('Failed to update settings');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={{ maxWidth: '640px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <SettingsIcon size={24} color="#06b6d4" />
          System Configuration Settings
        </h1>
        <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '4px' }}>
          Configure AI confidence thresholds, document category definitions, and routing parameters.
        </p>
      </div>

      <div className="glass-panel" style={{ padding: '32px' }}>
        {message && (
          <div style={{ background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', padding: '12px', color: '#34d399', fontSize: '0.85rem', marginBottom: '20px' }}>
            {message}
          </div>
        )}

        <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Threshold Slider */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <label style={{ fontSize: '0.9rem', fontWeight: 600, color: '#f8fafc' }}>
                AI Verification Confidence Threshold (%)
              </label>
              <span style={{ fontSize: '1.1rem', fontWeight: 700, color: '#06b6d4' }}>
                {confidenceThreshold}%
              </span>
            </div>
            <p style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '12px' }}>
              Documents with AI classification confidence below this percentage will be automatically routed to the Human Verification Queue.
            </p>
            <input
              type="range"
              min="0"
              max="99"
              step="1"
              value={confidenceThreshold}
              onChange={(e) => setConfidenceThreshold(e.target.value)}
              style={{ width: '100%', accentColor: '#06b6d4', cursor: 'pointer' }}
            />
          </div>

          {/* Categories List */}
          <div style={{ paddingTop: '16px', borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
            <label style={{ fontSize: '0.9rem', fontWeight: 600, color: '#f8fafc', display: 'block', marginBottom: '8px' }}>
              Model Categories (fixed by the trained model)
            </label>
            <p style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '12px' }}>
              Active model: {modelName}
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
              {categories.map((cat) => (
                <span key={cat} className={`badge cat-${cat.toLowerCase()}`} style={{ padding: '6px 14px', fontSize: '0.8rem' }}>
                  {cat}
                </span>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={saving}
            style={{
              padding: '12px',
              background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
              border: 'none',
              borderRadius: '8px',
              color: '#ffffff',
              fontWeight: 600,
              fontSize: '0.9rem',
              cursor: saving ? 'not-allowed' : 'pointer',
              boxShadow: '0 4px 15px rgba(6, 182, 212, 0.3)'
            }}
          >
            {saving ? 'Saving Settings...' : 'Save Configuration'}
          </button>
        </form>
      </div>
    </div>
  );
};
