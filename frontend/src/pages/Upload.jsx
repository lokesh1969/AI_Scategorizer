import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Upload as UploadIcon, FileText, CheckCircle2, AlertCircle, Sparkles, Cpu } from 'lucide-react';

export const Upload = () => {
  const [file, setFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progressStep, setProgressStep] = useState(0);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const pipelineSteps = [
    'Uploading document file...',
    'Detecting file format & ingesting payload...',
    'Extracting document content (PDF/DOCX/XLSX/TXT)...',
    'Applying OpenCV image preprocessing & CLAHE contrast...',
    'Executing bilingual Tesseract OCR (eng + hin)...',
    'Detecting bilingual language (English / Hindi / Mixed)...',
    'Executing TF-IDF + ML Document Classification...',
    'Calculating Urgency & Priority Score (0-100)...',
    'Generating extractive AI summary & extracting entities...',
    'Determining department routing & completing persistence...'
  ];

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setError('');
    setProgressStep(0);

    // Simulate animated step transitions for processing feedback
    const interval = setInterval(() => {
      setProgressStep((prev) => {
        if (prev < pipelineSteps.length - 2) return prev + 1;
        return prev;
      });
    }, 450);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      clearInterval(interval);
      setProgressStep(pipelineSteps.length - 1);

      setTimeout(() => {
        navigate(`/documents/${res.data._id}`);
      }, 800);
    } catch (err) {
      clearInterval(interval);
      setError(err.response?.data?.detail || 'Document processing failed. Please check file format and try again.');
      setUploading(false);
    }
  };

  return (
    <div style={{ maxWidth: '720px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc' }}>
          Document Upload & Processing Pipeline
        </h1>
        <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '4px' }}>
          Upload PDF, DOCX, XLSX, TXT, PNG, or JPG files. Supports bilingual English & Hindi scanned documents.
        </p>
      </div>

      <div className="glass-panel" style={{ padding: '32px' }}>
        {error && (
          <div style={{ background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: '8px', padding: '12px', color: '#fda4af', fontSize: '0.85rem', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        {!uploading ? (
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              style={{
                border: dragOver ? '2px dashed #06b6d4' : '2px dashed rgba(255, 255, 255, 0.15)',
                borderRadius: '12px',
                padding: '48px 24px',
                textAlign: 'center',
                background: dragOver ? 'rgba(6, 182, 212, 0.08)' : 'rgba(15, 23, 42, 0.5)',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              <input
                type="file"
                id="file-upload-input"
                onChange={handleFileChange}
                accept=".pdf,.docx,.xlsx,.txt,.png,.jpg,.jpeg"
                style={{ display: 'none' }}
              />
              <label htmlFor="file-upload-input" style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                <div style={{ width: '56px', height: '56px', borderRadius: '50%', background: 'rgba(6, 182, 212, 0.12)', border: '1px solid rgba(6, 182, 212, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <UploadIcon size={28} color="#06b6d4" />
                </div>
                <div>
                  <div style={{ fontSize: '1rem', fontWeight: 600, color: '#f8fafc' }}>
                    {file ? file.name : 'Drop your document here, or Browse Files'}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '4px' }}>
                    Supported: PDF, DOCX, XLSX, TXT, PNG, JPG (Max 25MB)
                  </div>
                </div>
              </label>
            </div>

            {file && (
              <div style={{ background: 'rgba(6, 182, 212, 0.1)', padding: '12px 16px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#67e8f9' }}>
                  <FileText size={18} />
                  <span>{file.name} ({(file.size / (1024*1024)).toFixed(2)} MB)</span>
                </div>
                <button type="button" onClick={() => setFile(null)} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
                  Remove
                </button>
              </div>
            )}

            <button
              type="submit"
              disabled={!file}
              style={{
                padding: '12px',
                background: file ? 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)' : 'rgba(255, 255, 255, 0.05)',
                border: 'none',
                borderRadius: '8px',
                color: file ? '#ffffff' : '#64748b',
                fontWeight: 600,
                fontSize: '0.9rem',
                cursor: file ? 'pointer' : 'not-allowed',
                boxShadow: file ? '0 4px 15px rgba(6, 182, 212, 0.3)' : 'none',
                transition: 'all 0.2s'
              }}
            >
              Start Intelligent Processing Pipeline
            </button>
          </form>
        ) : (
          /* Processing Steps Progress Animation */
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', padding: '12px 0' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ display: 'inline-flex', padding: '12px', borderRadius: '50%', background: 'rgba(6, 182, 212, 0.15)', marginBottom: '12px' }}>
                <Cpu size={32} color="#06b6d4" className="animate-spin" />
              </div>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                MetroMind Pipeline Execution
              </h2>
              <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '4px' }}>
                Processing document: {file?.name}
              </p>
            </div>

            {/* Progress Bar */}
            <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{ width: `${((progressStep + 1) / pipelineSteps.length) * 100}%`, height: '100%', background: 'linear-gradient(90deg, #06b6d4 0%, #8b5cf6 100%)', transition: 'width 0.3s ease' }}></div>
            </div>

            {/* Pipeline Stage Checklist */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '12px' }}>
              {pipelineSteps.map((step, idx) => {
                const isDone = idx < progressStep;
                const isCurrent = idx === progressStep;
                return (
                  <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.85rem', color: isDone ? '#34d399' : isCurrent ? '#06b6d4' : '#475569', fontWeight: isCurrent ? 600 : 400 }}>
                    {isDone ? <CheckCircle2 size={16} color="#10b981" /> : isCurrent ? <Sparkles size={16} color="#06b6d4" /> : <div style={{ width: '16px' }} />}
                    <span>{step}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
