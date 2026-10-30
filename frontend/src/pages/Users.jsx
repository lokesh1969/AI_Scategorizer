import React, { useEffect, useState } from 'react';
import { UserPlus, X } from 'lucide-react';
import api from '../services/api';
import { ALL_ROLES } from '../constants';
import { ROLE_NAMES } from '../components/Tags';
import { useAuth } from '../context/AuthContext';

export const Users = () => {
  const { user: me } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [message, setMessage] = useState(null); // { kind: 'ok' | 'error', text }

  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('UPLOADER');
  const [submitting, setSubmitting] = useState(false);

  const fetchUsers = () =>
    api
      .get('/users')
      .then((res) => setUsers(res.data))
      .catch(() => setMessage({ kind: 'error', text: 'Users could not be loaded.' }))
      .finally(() => setLoading(false));

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage(null);
    try {
      await api.post('/users', { email, name, password, role });
      setMessage({ kind: 'ok', text: `${name} (${email}) can now sign in as ${ROLE_NAMES[role]}.` });
      setShowCreate(false);
      setEmail('');
      setName('');
      setPassword('');
      setRole('UPLOADER');
      fetchUsers();
    } catch (err) {
      const detail = err.response?.data?.detail;
      setMessage({
        kind: 'error',
        text: Array.isArray(detail) ? 'Check the fields: a valid email and a password of at least 8 characters are required.' : detail || 'The user could not be created.',
      });
    } finally {
      setSubmitting(false);
    }
  };

  const update = async (u, changes, okText) => {
    setMessage(null);
    try {
      await api.patch(`/users/${u._id}`, changes);
      setMessage({ kind: 'ok', text: okText });
      fetchUsers();
    } catch {
      setMessage({ kind: 'error', text: `${u.name} could not be updated.` });
    }
  };

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1 className="page-title">Users</h1>
          <p className="page-lede">Who can sign in, and which desk each person works at. Role changes take effect at their next request.</p>
        </div>
        {!showCreate && (
          <button type="button" className="btn btn-primary" onClick={() => setShowCreate(true)}>
            <UserPlus size={18} aria-hidden="true" /> Add a user
          </button>
        )}
      </div>

      {message && (
        <div className={`notice ${message.kind === 'ok' ? 'notice-ok' : 'notice-error'}`} role={message.kind === 'ok' ? 'status' : 'alert'}>
          <span>{message.text}</span>
        </div>
      )}

      {showCreate && (
        <section className="panel" aria-labelledby="create-title">
          <div className="panel-head">
            <h2 id="create-title" className="section-title">Add a user</h2>
            <button type="button" className="icon-btn" aria-label="Close" onClick={() => setShowCreate(false)}>
              <X size={18} />
            </button>
          </div>
          <form className="panel-body create-user" onSubmit={handleCreate}>
            <div className="field">
              <label htmlFor="nu-name">Full name</label>
              <input id="nu-name" className="input" required value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div className="field">
              <label htmlFor="nu-email">Email</label>
              <input id="nu-email" className="input" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="name@aiscategorizer.local" />
            </div>
            <div className="field">
              <label htmlFor="nu-pass">Password</label>
              <input id="nu-pass" className="input" type="password" required minLength={8} autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} />
              <span className="hint">At least 8 characters.</span>
            </div>
            <div className="field">
              <label htmlFor="nu-role">Role</label>
              <select id="nu-role" className="select" value={role} onChange={(e) => setRole(e.target.value)}>
                {ALL_ROLES.map((r) => <option key={r} value={r}>{ROLE_NAMES[r]}</option>)}
              </select>
            </div>
            <div className="actions">
              <button type="button" className="btn" onClick={() => setShowCreate(false)}>Cancel</button>
              <button type="submit" className="btn btn-primary" disabled={submitting}>{submitting ? 'Adding…' : 'Add user'}</button>
            </div>
          </form>
        </section>
      )}

      <div className="panel">
        {loading ? (
          <div className="loading">Loading users…</div>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th scope="col">Name</th>
                  <th scope="col">Email</th>
                  <th scope="col">Role</th>
                  <th scope="col">Status</th>
                  <th scope="col"><span className="visually-hidden">Actions</span></th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => {
                  const active = u.is_active !== false;
                  // You cannot lock yourself out: no self-deactivation or self-demotion
                  const isMe = u._id === me?.id;
                  return (
                    <tr key={u._id}>
                      <td className="cell-strong">{u.name}{isMe && <span className="hint"> (you)</span>}</td>
                      <td className="muted">{u.email}</td>
                      <td>
                        <label htmlFor={`role-${u._id}`} className="visually-hidden">Role for {u.name}</label>
                        <select
                          id={`role-${u._id}`}
                          className="select"
                          style={{ minWidth: 190 }}
                          value={u.role}
                          disabled={isMe}
                          onChange={(e) => update(u, { role: e.target.value }, `${u.name} is now ${ROLE_NAMES[e.target.value]}.`)}
                        >
                          {ALL_ROLES.map((r) => <option key={r} value={r}>{ROLE_NAMES[r]}</option>)}
                        </select>
                      </td>
                      <td>
                        <span className={`chip ${active ? 'chip-routed' : 'chip-high'}`}>
                          <span className="chip-dot" aria-hidden="true" />
                          {active ? 'Active' : 'Deactivated'}
                        </span>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        {!isMe && (
                        <button
                          type="button"
                          className={`btn btn-sm${active ? ' btn-danger' : ''}`}
                          onClick={() => update(u, { is_active: !active }, `${u.name} ${active ? 'can no longer sign in' : 'can sign in again'}.`)}
                        >
                          {active ? 'Deactivate' : 'Reactivate'}
                        </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
