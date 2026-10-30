import React from 'react';
import { Check } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { ROLE_NAMES } from '../components/Tags';

const PERMISSIONS = {
  ADMIN: [
    'See every document in every department',
    'Upload documents',
    'Check documents in the manual-check queue, and re-route any document',
    'Add, deactivate and change the role of users',
    'Read the audit log',
    'Set the confidence threshold',
  ],
  FINANCE_MANAGER: [
    'See Finance documents (invoices, budgets, payments)',
    'Check documents in the manual-check queue',
    'See summaries, amounts and other details found in each document',
  ],
  HR_MANAGER: [
    'See HR documents (resumes, leave, policies)',
    'Check documents in the manual-check queue',
    'See summaries and details found in each document',
  ],
  LEGAL_COUNSEL: [
    'See Legal documents (contracts, notices, compliance)',
    'Check documents in the manual-check queue',
    'See summaries and details found in each document',
  ],
  OPERATIONS_MANAGER: [
    'See Operations documents (logistics, reports, memos)',
    'Check documents in the manual-check queue',
    'See summaries and details found in each document',
  ],
  UPLOADER: [
    'Upload documents',
    'See only the documents you uploaded, and where each one went',
  ],
};

export const Profile = () => {
  const { user } = useAuth();
  if (!user) return null;
  const perms = PERMISSIONS[user.role] || [];

  return (
    <div className="page page-narrow">
      <div className="page-head">
        <h1 className="page-title">My profile</h1>
      </div>

      <section className="panel panel-body" style={{ display: 'flex', gap: 20, alignItems: 'center', flexWrap: 'wrap' }}>
        <span className="avatar" aria-hidden="true">{user.name?.charAt(0)}</span>
        <div style={{ minWidth: 0 }}>
          <h2 className="section-title" style={{ fontSize: '1.35rem' }}>{user.name}</h2>
          <div className="muted">{user.email}</div>
          <span className="chip chip-role" style={{ marginTop: 8 }}>{ROLE_NAMES[user.role] || user.role}</span>
        </div>
      </section>

      <section className="panel panel-body" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <h2 className="section-title">What you can do</h2>
        <ul className="perm-list">
          {perms.map((p) => (
            <li key={p}>
              <Check size={18} aria-hidden="true" />
              <span>{p}</span>
            </li>
          ))}
        </ul>
        <p className="hint">These rules are enforced by the server, so they hold even outside this interface.</p>
      </section>
    </div>
  );
};
