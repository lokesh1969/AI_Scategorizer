// Mirrors backend/app/core/categories.py — keep the two in sync.
export const API_ORIGIN = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const CATEGORIES = ['FINANCE', 'HR', 'LEGAL', 'OPERATIONS'];

export const DEPARTMENTS = {
  FINANCE: 'Finance Manager',
  HR: 'HR Manager',
  LEGAL: 'Legal Counsel',
  OPERATIONS: 'Operations Manager',
};

export const CATEGORY_COLORS = {
  FINANCE: '#10b981',
  HR: '#8b5cf6',
  LEGAL: '#f59e0b',
  OPERATIONS: '#06b6d4',
  UNCLASSIFIED: '#94a3b8',
};

export const REVIEWER_ROLES = ['FINANCE_MANAGER', 'HR_MANAGER', 'LEGAL_COUNSEL', 'OPERATIONS_MANAGER'];
export const ALL_ROLES = ['ADMIN', ...REVIEWER_ROLES, 'UPLOADER'];

export const ROLE_LABELS = {
  ADMIN: 'System Admin',
  FINANCE_MANAGER: 'Finance Manager',
  HR_MANAGER: 'HR Manager',
  LEGAL_COUNSEL: 'Legal Counsel',
  OPERATIONS_MANAGER: 'Operations Manager',
  UPLOADER: 'Document Uploader',
};
