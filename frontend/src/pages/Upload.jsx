import React, { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileUp, FileText, CheckCircle2, AlertCircle, X } from 'lucide-react';
import api from '../services/api';

// What the server does with each upload, in order. The server runs them in one
// request, so the checklist advances on a timer and completes when it answers.
const STEPS = [
  'Receiving the file',
  'Checking type and size',
  'Reading the text (OCR for scans)',
  'Detecting the language',
  'Scoring it against each department',
  'Setting priority, summary and key details',
  'Checking confidence and routing',
];

const MAX_MB = 25;

export const Upload = () => {
  const [file, setFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [step, setStep] = useState(0);
  const [error, setError] = useState('');
  const inputRef = useRef(null);
  const navigate = useNavigate();

  const choose = (f) => {
    if (!f) return;
    if (f.size > MAX_MB * 1024 * 1024) {
      setError(`"${f.name}" is ${(f.size / 1048576).toFixed(1)} MB. The limit is ${MAX_MB} MB.`);
      return;
    }
    setFile(f);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setError('');
    setStep(0);
    const timer = setInterval(() => setStep((s) => Math.min(s + 1, STEPS.length - 2)), 500);

    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await api.post('/documents/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
      clearInterval(timer);
      setStep(STEPS.length);
      setTimeout(() => navigate(`/documents/${res.data._id}`), 700);
    } catch (err) {
      clearInterval(timer);
      setError(err.response?.data?.detail || 'The document could not be processed. Check the file type and try again.');
      setUploading(false);
    }
  };

  return (
    <div className="page page-narrow">
      <div className="page-head">
        <div>
          <h1 className="page-title">Upload a document</h1>
          <p className="page-lede">
            PDF, Word (.docx), Excel (.xlsx), text, or a PNG/JPG photo or scan, up to {MAX_MB} MB. English and Hindi are both read.
          </p>
        </div>
      </div>

      <div className="panel panel-body" style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
        {error && (
          <div className="notice notice-error" role="alert">
            <AlertCircle size={18} aria-hidden="true" />
            <span>{error}</span>
          </div>
        )}

        {!uploading ? (
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <label
              htmlFor="file-upload-input"
              className={`dropzone${dragOver ? ' is-over' : ''}`}
              onDragOver={(e) => {
                e.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragOver(false);
                choose(e.dataTransfer.files?.[0]);
              }}
            >
              <input
                ref={inputRef}
                id="file-upload-input"
                type="file"
                className="visually-hidden"
                accept=".pdf,.docx,.xlsx,.txt,.png,.jpg,.jpeg"
                onChange={(e) => choose(e.target.files?.[0])}
              />
              <span className="dropzone-icon" aria-hidden="true"><FileUp size={26} /></span>
              <span className="dropzone-title">Drop a file here, or choose one</span>
              <span className="hint">It is read, tagged and routed as soon as you start.</span>
            </label>

            {file && (
              <div className="file-chip">
                <span><FileText size={18} aria-hidden="true" />{file.name} <span className="hint num">({(file.size / 1048576).toFixed(2)} MB)</span></span>
                <button
                  type="button"
                  className="icon-btn"
                  aria-label="Remove file"
                  onClick={() => {
                    setFile(null);
                    if (inputRef.current) inputRef.current.value = '';
                  }}
                >
                  <X size={18} />
                </button>
              </div>
            )}

            <button type="submit" className="btn btn-primary btn-lg" disabled={!file}>
              Read, tag and route it
            </button>
          </form>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }} aria-live="polite">
            <div>
              <h2 className="section-title">Processing {file?.name}</h2>
              <p className="hint">Scans take longer because every page is cleaned up and read with OCR.</p>
            </div>
            <div className="progress" aria-hidden="true">
              <span style={{ width: `${(Math.min(step + 1, STEPS.length) / STEPS.length) * 100}%` }} />
            </div>
            <ol className="pipeline">
              {STEPS.map((label, i) => {
                const done = i < step;
                const current = i === step;
                return (
                  <li key={label} className={done ? 'is-done' : current ? 'is-current' : ''}>
                    {done ? <CheckCircle2 size={18} aria-hidden="true" /> : <span className="pipeline-dot" aria-hidden="true" />}
                    <span>{label}</span>
                  </li>
                );
              })}
            </ol>
          </div>
        )}
      </div>
    </div>
  );
};
