import React from 'react';
import { useAuth } from '../context/AuthContext';
import { User, Shield, CheckCircle2, Key } from 'lucide-react';

export const Profile = () => {
  const { user } = useAuth();
  if (!user) return null;

  const permissionsMap = {
    ADMIN: [
      'Access ALL system documents across departments',
      'Upload new documents and trigger processing',
      'Perform human verification & re-classify documents',
      'Create, edit, and deactivate user accounts',
      'View system-wide security audit logs',
      'Configure AI confidence thresholds & system settings'
    ],
    FINANCE_MANAGER: [
      'Access FINANCE department documents (invoices, budgets, payments)',
      'Review and verify documents in the human verification queue',
      'View document AI summaries, extracted amounts, and entities',
      'Access department dashboard'
    ],
    HR_MANAGER: [
      'Access HR department documents (resumes, leave, policies)',
      'Review and verify documents in the human verification queue',
      'View document AI summaries, entities, and sentiment',
      'Access department dashboard'
    ],
    LEGAL_COUNSEL: [
      'Access LEGAL department documents (contracts, notices, compliance)',
      'Review and verify documents in the human verification queue',
      'View document AI summaries, entities, and priority',
      'Access department dashboard'
    ],
    OPERATIONS_MANAGER: [
      'Access OPERATIONS department documents (logistics, reports, memos)',
      'Review and verify documents in the human verification queue',
      'View document AI summaries, entities, and priority',
      'Access department dashboard'
    ],
    UPLOADER: [
      'Upload new documents to AI Scategorizer processing engine',
      'View ONLY self-uploaded documents and telemetry results',
      'View self-document summaries, OCR text, and classification',
      'Access personal dashboard analytics'
    ]
  };

  const currentPermissions = permissionsMap[user.role] || [];

  return (
    <div style={{ maxWidth: '640px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <User size={24} color="#06b6d4" />
          User Profile & Role Authorization
        </h1>
        <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '4px' }}>
          Authenticated session details and Role-Based Access Control (RBAC) privileges.
        </p>
      </div>

      <div className="glass-panel" style={{ padding: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '24px', paddingBottom: '20px', borderBottom: '1px solid rgba(255, 255, 255, 0.08)' }}>
          <div style={{ width: '64px', height: '64px', borderRadius: '50%', background: 'linear-gradient(135deg, #06b6d4 0%, #8b5cf6 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', fontWeight: 700, color: '#fff' }}>
            {user.name?.charAt(0)}
          </div>
          <div>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
              {user.name}
            </h2>
            <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '2px' }}>
              {user.email}
            </div>
            <div style={{ marginTop: '8px' }}>
              <span className="badge badge-verified">
                {user.role}
              </span>
            </div>
          </div>
        </div>

        <div>
          <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#f8fafc', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Shield size={18} color="#10b981" />
            Assigned Role Authorization Privileges
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {currentPermissions.map((perm, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.85rem', color: '#cbd5e1' }}>
                <CheckCircle2 size={16} color="#10b981" style={{ flexShrink: 0 }} />
                <span>{perm}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
