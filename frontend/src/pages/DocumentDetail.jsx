import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { 
  FileText, 
  Sparkles, 
  AlertTriangle, 
  CheckCircle2, 
  Shield, 
  Layers, 
  Tag, 
  Smile, 
  Frown, 
  Meh, 
  Cpu, 
  Image as ImageIcon,
  ArrowLeft,
  User,
  Clock,
  ExternalLink
} from 'lucide-react';

export const DocumentDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [doc, setDoc] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Verification Form State
  const [verifiedCategory, setVerifiedCategory] = useState('');
  const [verificationNotes, setVerificationNotes] = useState('');
  const [submittingVerification, setSubmittingVerification] = useState(false);

  // Image Preview Toggle (Original vs Preprocessed)
  const [showPreprocessed, setShowPreprocessed] = useState(true);

  useEffect(() => {
    fetchDocument();
  }, [id]);

  const fetchDocument = async () => {
    try {
      const res = await api.get(`/documents/${id}`);
      setDoc(res.data);
      setVerifiedCategory(res.data.classification?.predicted_category || 'SAFETY');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load document details');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifySubmit = async (e) => {
    e.preventDefault();
    setSubmittingVerification(true);
    try {
      const res = await api.post(`/verification/verify/${id}`, {
        verified_category: verifiedCategory,
        notes: verificationNotes
      });
      alert('Human verification submitted successfully!');
      fetchDocument();
    } catch (err) {
      alert(err.response?.data?.detail || 'Verification submission failed');
    } finally {
      setSubmittingVerification(false);
    }
  };

  if (loading) return <div style={{ padding: '40px', color: '#94a3b8' }}>Loading document details...</div>;
  if (error) return <div style={{ padding: '40px', color: '#f43f5e' }}>{error}</div>;
  if (!doc) return null;

  const probs = doc.classification?.probabilities || {};
  const isHumanReq = doc.verification_status === 'HUMAN VERIFICATION REQUIRED';

  const canVerify = ['ADMIN', 'STATION_CONTROLLER', 'FINANCE_MANAGER', 'MAINTENANCE_HEAD'].includes(user?.role);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button 
            onClick={() => navigate(-1)} 
            style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '8px', color: '#94a3b8', cursor: 'pointer' }}
          >
            <ArrowLeft size={20} />
          </button>
          <div>
            <h1 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#f8fafc' }}>
              {doc.original_filename}
            </h1>
            <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span>ID: {doc._id}</span>
              <span>•</span>
              <span>Type: {doc.file_type}</span>
              <span>•</span>
              <span>Language: <strong style={{ color: '#06b6d4' }}>{doc.language}</strong></span>
              <span>•</span>
              <span>Uploaded {new Date(doc.upload_timestamp).toLocaleString()}</span>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span className={`badge ${doc.verification_status === 'AI VERIFIED' ? 'badge-verified' : 'badge-human-req'}`}>
            {doc.verification_status}
          </span>
          <span className={`badge badge-${doc.priority?.level?.toLowerCase()}`}>
            {doc.priority?.level} PRIORITY
          </span>
        </div>
      </div>

      {/* Human Verification Alert Banner */}
      {isHumanReq && (
        <div className="glass-panel-glow" style={{ padding: '20px', background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.4)' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
            <AlertTriangle size={24} color="#f59e0b" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div style={{ flex: 1 }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#fbbf24' }}>
                Human Verification Required
              </h3>
              <p style={{ fontSize: '0.85rem', color: '#cbd5e1', marginTop: '4px' }}>
                AI classification confidence ({doc.classification?.confidence}%) is below the configured system threshold (70.0%). This document has been routed to the Human Verification Queue for manual review and category confirmation.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 2-Column Main Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '24px' }}>
        {/* Left Column: AI Classification & Telemetry */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* AI Classification & Probability Gauge */}
          <div className="glass-panel" style={{ padding: '24px' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={20} color="#06b6d4" />
              AI Classification & Probability Distribution
            </h2>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px' }}>
              <div>
                <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>Predicted Category</div>
                <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#f8fafc', marginTop: '2px' }}>
                  {doc.classification?.predicted_category}
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>Confidence Score</div>
                <div style={{ fontSize: '1.4rem', fontWeight: 700, color: doc.classification?.confidence >= 70 ? '#34d399' : '#fbbf24', marginTop: '2px' }}>
                  {doc.classification?.confidence}%
                </div>
              </div>
            </div>

            {/* Probability Distribution Bars */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#94a3b8' }}>Class Probabilities</div>
              {Object.entries(probs).map(([cat, prob]) => {
                const isTop = cat === doc.classification?.predicted_category;
                return (
                  <div key={cat}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: isTop ? '#f8fafc' : '#94a3b8', fontWeight: isTop ? 600 : 400, marginBottom: '4px' }}>
                      <span>{cat}</span>
                      <span>{prob}%</span>
                    </div>
                    <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.06)', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ width: `${prob}%`, height: '100%', background: isTop ? '#06b6d4' : '#475569', transition: 'width 0.4s' }}></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Priority Score & Reasoning */}
          <div className="glass-panel" style={{ padding: '24px' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Shield size={20} color="#f43f5e" />
              Urgency & Priority Telemetry
            </h2>

            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
              <div style={{
                width: '64px',
                height: '64px',
                borderRadius: '50%',
                background: 'rgba(244, 63, 94, 0.15)',
                border: '2px solid #f43f5e',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.25rem',
                fontWeight: 800,
                color: '#fb7185'
              }}>
                {doc.priority?.score}
              </div>

              <div>
                <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>Priority Level</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                  {doc.priority?.level}
                </div>
              </div>
            </div>

            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '12px 16px', borderRadius: '8px', fontSize: '0.85rem', color: '#cbd5e1', borderLeft: '3px solid #f43f5e' }}>
              <strong style={{ color: '#f8fafc' }}>Reason: </strong>
              {doc.priority?.reason}
            </div>
          </div>

          {/* AI Summary */}
          <div className="glass-panel" style={{ padding: '24px' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={20} color="#8b5cf6" />
              Bilingual AI Executive Summary
            </h2>
            <div style={{ fontSize: '0.9rem', color: '#cbd5e1', lineHeight: '1.6', whiteSpace: 'pre-line', background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '8px' }}>
              {doc.summary}
            </div>
          </div>
        </div>

        {/* Right Column: OCR Preprocessing, Entities, Sentiment, & Verification */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Extracted Entities & Sentiment */}
          <div className="glass-panel" style={{ padding: '24px' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Tag size={20} color="#10b981" />
              Extracted Named Entities (NER) & Sentiment
            </h2>

            {/* Sentiment Gauge */}
            <div style={{ display: 'flex', alignItems: 'center', justifyBetween: 'space-between', marginBottom: '20px', background: 'rgba(15, 23, 42, 0.6)', padding: '12px 16px', borderRadius: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {doc.sentiment?.label === 'POSITIVE' && <Smile size={20} color="#10b981" />}
                {doc.sentiment?.label === 'NEGATIVE' && <Frown size={20} color="#f43f5e" />}
                {doc.sentiment?.label === 'NEUTRAL' && <Meh size={20} color="#94a3b8" />}
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f8fafc' }}>
                  Sentiment: {doc.sentiment?.label}
                </span>
              </div>
              <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                Score: {doc.sentiment?.score}
              </span>
            </div>

            {/* Entity Chips */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {doc.entities?.length === 0 ? (
                <span style={{ fontSize: '0.85rem', color: '#64748b' }}>No entities extracted.</span>
              ) : (
                doc.entities?.map((ent, idx) => (
                  <span 
                    key={idx} 
                    style={{
                      background: 'rgba(6, 182, 212, 0.12)',
                      border: '1px solid rgba(6, 182, 212, 0.3)',
                      borderRadius: '16px',
                      padding: '4px 10px',
                      fontSize: '0.75rem',
                      color: '#67e8f9',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    <strong style={{ color: '#06b6d4' }}>{ent.label}:</strong>
                    <span>{ent.text}</span>
                  </span>
                ))
              )}
            </div>
          </div>

          {/* OCR & Image Preprocessing Pipeline Preview */}
          <div className="glass-panel" style={{ padding: '24px' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Cpu size={20} color="#06b6d4" />
              OCR Engine & Preprocessing Telemetry
            </h2>

            <div style={{ fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '12px' }}>
              <div><strong>OCR Used:</strong> {doc.ocr_metadata?.ocr_used ? 'Yes (Tesseract OCR eng+hin)' : 'No (Digital Text Directly Extracted)'}</div>
              {doc.ocr_metadata?.preprocessing_applied?.length > 0 && (
                <div style={{ marginTop: '8px' }}>
                  <strong>Applied Preprocessing Filters:</strong>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '6px' }}>
                    {doc.ocr_metadata.preprocessing_applied.map((step, i) => (
                      <span key={i} style={{ background: 'rgba(255,255,255,0.06)', padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', color: '#94a3b8' }}>
                        {step}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Image Preview Toggle */}
            {doc.ocr_metadata?.preprocessed_image_url && (
              <div style={{ marginTop: '16px', textAlign: 'center' }}>
                <img 
                  src={`http://localhost:8000${doc.ocr_metadata.preprocessed_image_url}`} 
                  alt="Preprocessed Preview" 
                  style={{ maxWidth: '100%', maxHeight: '240px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)' }}
                />
                <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '6px' }}>
                  OpenCV Preprocessed Image (Grayscale + CLAHE + Denoised + Otsu Binarized)
                </div>
              </div>
            )}
          </div>

          {/* Raw Extracted Text Viewer */}
          <div className="glass-panel" style={{ padding: '24px' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', marginBottom: '12px' }}>
              Raw Extracted Text (UTF-8)
            </h2>
            <textarea
              readOnly
              value={doc.extracted_text}
              style={{
                width: '100%',
                height: '160px',
                background: 'rgba(9, 13, 22, 0.9)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                padding: '12px',
                color: '#f8fafc',
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '0.8rem',
                outline: 'none',
                resize: 'vertical'
              }}
            />
          </div>

          {/* Human Verification Action Form (For Authorized Roles) */}
          {canVerify && (
            <div className="glass-panel" style={{ padding: '24px', border: '1px solid rgba(6, 182, 212, 0.4)' }}>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={20} color="#10b981" />
                Human Verification Control
              </h2>

              <form onSubmit={handleVerifySubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div>
                  <label style={{ fontSize: '0.8rem', fontWeight: 500, color: '#cbd5e1', display: 'block', marginBottom: '6px' }}>
                    Confirm or Modify Target Category
                  </label>
                  <select
                    value={verifiedCategory}
                    onChange={(e) => setVerifiedCategory(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      background: 'rgba(15, 23, 42, 0.8)',
                      border: '1px solid rgba(255, 255, 255, 0.12)',
                      borderRadius: '8px',
                      color: '#f8fafc',
                      fontSize: '0.875rem',
                      outline: 'none'
                    }}
                  >
                    <option value="SAFETY">SAFETY (Route to Station Controller)</option>
                    <option value="OPERATIONS">OPERATIONS (Route to Station Controller)</option>
                    <option value="FINANCE">FINANCE (Route to Finance Manager)</option>
                    <option value="MAINTENANCE">MAINTENANCE (Route to Maintenance Head)</option>
                  </select>
                </div>

                <div>
                  <label style={{ fontSize: '0.8rem', fontWeight: 500, color: '#cbd5e1', display: 'block', marginBottom: '6px' }}>
                    Verification Notes & Audit Remarks
                  </label>
                  <textarea
                    value={verificationNotes}
                    onChange={(e) => setVerificationNotes(e.target.value)}
                    placeholder="Enter notes explaining verification rationale..."
                    rows={3}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      background: 'rgba(15, 23, 42, 0.8)',
                      border: '1px solid rgba(255, 255, 255, 0.12)',
                      borderRadius: '8px',
                      color: '#f8fafc',
                      fontSize: '0.85rem',
                      outline: 'none'
                    }}
                  />
                </div>

                <button
                  type="submit"
                  disabled={submittingVerification}
                  style={{
                    padding: '12px',
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#ffffff',
                    fontWeight: 600,
                    fontSize: '0.9rem',
                    cursor: submittingVerification ? 'not-allowed' : 'pointer',
                    boxShadow: '0 4px 15px rgba(16, 185, 129, 0.3)'
                  }}
                >
                  {submittingVerification ? 'Submitting Verification...' : 'Approve & Confirm Classification'}
                </button>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
