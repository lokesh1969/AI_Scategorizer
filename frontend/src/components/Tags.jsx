import React from 'react';
import { DEPARTMENTS } from '../constants';

// Three-letter destination codes printed on every tag
export const DEST_CODES = {
  FINANCE: 'FIN',
  HR: 'HR',
  LEGAL: 'LEG',
  OPERATIONS: 'OPS',
};

const TAG_CLASS = { FIN: 'dtag-fin', HR: 'dtag-hr', LEG: 'dtag-leg', OPS: 'dtag-ops' };

export const isManualCheck = (status) => status === 'HUMAN VERIFICATION REQUIRED';

/**
 * A destination tag: department code on its colour stripe plus the model's confidence.
 * Documents waiting for a person get the yellow manual-check tag instead.
 */
export const DestTag = ({ category, confidence, status, size = 'sm', sub, barcode }) => {
  const manual = isManualCheck(status);
  const code = DEST_CODES[category] || '???';
  const cls = manual ? 'dtag-check' : TAG_CLASS[code] || '';
  // After a person decides, the model's score no longer describes the destination
  const checked = status === 'HUMAN VERIFIED';
  const conf = checked ? 'Checked' : typeof confidence === 'number' ? `${confidence.toFixed(1)}%` : '—';
  const label = manual
    ? `Manual check. Model guess ${category || 'unknown'} at ${conf}`
    : checked
      ? `Destination ${DEPARTMENTS[category] || category}, decided by a reviewer`
      : `Destination ${DEPARTMENTS[category] || category || 'unknown'}, confidence ${conf}`;

  return (
    <span className={`dtag dtag-${size} ${cls}`} role="img" aria-label={label}>
      <span className="dtag-code">
        <span>{manual ? 'CHK' : code}</span>
      </span>
      <span className="dtag-meta">
        <span className="dtag-conf">{conf}</span>
        {size !== 'sm' && (
          <span className="dtag-sub">
            {sub || (manual ? `Model guess: ${code}` : DEPARTMENTS[category] || 'Unclassified')}
          </span>
        )}
        {barcode && <span className="dtag-barcode" aria-hidden="true" />}
      </span>
    </span>
  );
};

const STATUS_LABELS = {
  'AI VERIFIED': { text: 'Routed by AI', cls: 'chip-routed' },
  'HUMAN VERIFICATION REQUIRED': { text: 'Manual check', cls: 'chip-check' },
  'HUMAN VERIFIED': { text: 'Checked by reviewer', cls: 'chip-human' },
};

export const StatusChip = ({ status }) => {
  const s = STATUS_LABELS[status] || { text: status || 'Unknown', cls: '' };
  return (
    <span className={`chip ${s.cls}`} title={status}>
      <span className="chip-dot" aria-hidden="true" />
      {s.text}
    </span>
  );
};

export const PriorityChip = ({ level }) => {
  if (!level) return null;
  const lvl = level.toLowerCase();
  return <span className={`chip chip-${lvl}`}>{level.charAt(0) + level.slice(1).toLowerCase()}</span>;
};

export const ROLE_NAMES = {
  ADMIN: 'Administrator',
  FINANCE_MANAGER: 'Finance Manager',
  HR_MANAGER: 'HR Manager',
  LEGAL_COUNSEL: 'Legal Counsel',
  OPERATIONS_MANAGER: 'Operations Manager',
  UPLOADER: 'Uploader',
};
