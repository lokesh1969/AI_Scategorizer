import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, ArrowRight, AlertCircle, Mail, Lock } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { BrandMark } from '../components/BrandMark';
import '../styles/login.css';

// Demo accounts seeded by the backend (scripts/seed_db.py); code = the desk they work at
const DEMO_ACCOUNTS = [
  { label: 'Administrator', email: 'admin@aiscategorizer.local', pass: 'admin123', code: 'ADM', note: 'Everything, plus users and settings' },
  { label: 'Finance Manager', email: 'finance@aiscategorizer.local', pass: 'finance123', code: 'FIN', note: 'Finance desk and the manual-check queue' },
  { label: 'HR Manager', email: 'hr@aiscategorizer.local', pass: 'hr123', code: 'HR', note: 'HR desk and the manual-check queue' },
  { label: 'Legal Counsel', email: 'legal@aiscategorizer.local', pass: 'legal123', code: 'LEG', note: 'Legal desk and the manual-check queue' },
  { label: 'Operations Manager', email: 'operations@aiscategorizer.local', pass: 'ops123', code: 'OPS', note: 'Operations desk and the manual-check queue' },
  { label: 'Uploader', email: 'uploader@aiscategorizer.local', pass: 'user123', code: 'UPL', note: 'Uploads documents, sees their own' },
];

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const pickDemo = (acc) => {
    setEmail(acc.email);
    setPassword(acc.pass);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Sign-in failed. Check the email and password and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signin">
      <aside className="signin-side">
        <Link to="/" className="brand">
          <BrandMark />
          <span className="brand-name">AI Scategorizer</span>
        </Link>
        <div className="signin-pitch">
          <h1 className="display">Every document to the right desk.</h1>
          <p>Sign in as any role to see the same document from each side: the uploader, the department, and the reviewer who checks the unsure ones.</p>
        </div>
        <Link to="/" className="signin-back">
          <ArrowLeft size={16} aria-hidden="true" />
          Back to the overview
        </Link>
      </aside>

      <section className="signin-main">
        <div className="signin-box">
          <h2 className="page-title">Sign in</h2>

          {error && (
            <div className="notice notice-error" role="alert" style={{ marginTop: 20 }}>
              <AlertCircle size={18} aria-hidden="true" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="signin-form">
            <div className="field">
              <label htmlFor="email">Email</label>
              <div className="input-icon">
                <Mail size={18} aria-hidden="true" />
                <input
                  id="email"
                  className="input"
                  type="email"
                  autoComplete="username"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@aiscategorizer.local"
                  required
                />
              </div>
            </div>
            <div className="field">
              <label htmlFor="password">Password</label>
              <div className="input-icon">
                <Lock size={18} aria-hidden="true" />
                <input
                  id="password"
                  className="input"
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>
            <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
              {loading ? 'Signing in…' : (<>Sign in <ArrowRight size={18} aria-hidden="true" /></>)}
            </button>
          </form>

          <div className="demo">
            <h3 className="section-title">Demo accounts</h3>
            <p className="hint">Pick one to fill the form, then sign in.</p>
            <ul className="demo-list">
              {DEMO_ACCOUNTS.map((acc) => {
                const selected = email === acc.email;
                return (
                  <li key={acc.email}>
                    <button
                      type="button"
                      className={`demo-pick${selected ? ' is-selected' : ''}`}
                      onClick={() => pickDemo(acc)}
                      aria-pressed={selected}
                    >
                      <span className={`demo-code code-${acc.code.toLowerCase()}`}>{acc.code}</span>
                      <span className="demo-text">
                        <span className="demo-label">{acc.label}</span>
                        <span className="demo-note">{acc.note}</span>
                      </span>
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
};
