import React, { useEffect, useState } from 'react';
import { NavLink, Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  Upload,
  ClipboardCheck,
  Users,
  ScrollText,
  SlidersHorizontal,
  UserRound,
  LogOut,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { ALL_ROLES, REVIEWER_ROLES } from '../constants';
import api from '../services/api';
import { BrandMark } from './BrandMark';
import { ROLE_NAMES } from './Tags';

const NAV = [
  { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, roles: ALL_ROLES },
  { label: 'Documents', path: '/documents', icon: FileText, roles: ALL_ROLES },
  { label: 'Upload', path: '/upload', icon: Upload, roles: ['ADMIN', 'UPLOADER'] },
  { label: 'Manual check', path: '/verification', icon: ClipboardCheck, roles: ['ADMIN', ...REVIEWER_ROLES], queue: true },
  { label: 'Users', path: '/users', icon: Users, roles: ['ADMIN'] },
  { label: 'Audit log', path: '/audit-logs', icon: ScrollText, roles: ['ADMIN'] },
  { label: 'Settings', path: '/settings', icon: SlidersHorizontal, roles: ['ADMIN'] },
  { label: 'My profile', path: '/profile', icon: UserRound, roles: ALL_ROLES },
];

export const Sidebar = ({ onNavigate }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [queueCount, setQueueCount] = useState(null);
  const isReviewer = user && ['ADMIN', ...REVIEWER_ROLES].includes(user.role);

  // Keep the manual-check count fresh as the reviewer moves around the app
  useEffect(() => {
    if (!isReviewer) return;
    api
      .get('/verification')
      .then((res) => setQueueCount(res.data.length))
      .catch(() => setQueueCount(null));
  }, [isReviewer, location.pathname]);

  if (!user) return null;
  const items = NAV.filter((item) => item.roles.includes(user.role));

  return (
    <aside className="rail" aria-label="Main navigation">
      <Link to="/" className="brand" onClick={onNavigate}>
        <BrandMark />
        <span className="brand-name">AI Scategorizer</span>
      </Link>

      <nav className="rail-nav">
        {items.map(({ label, path, icon: Icon, queue }) => (
          <NavLink
            key={path}
            to={path}
            onClick={onNavigate}
            className={({ isActive }) => `rail-link${isActive ? ' active' : ''}`}
          >
            <Icon size={18} aria-hidden="true" />
            <span>{label}</span>
            {queue && queueCount > 0 && (
              <span className="rail-count num" aria-label={`${queueCount} waiting`}>{queueCount}</span>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="rail-foot">
        <div>
          <div className="rail-user-name">{user.name}</div>
          <div className="rail-user-mail">{user.email}</div>
        </div>
        <span className="rail-role">{ROLE_NAMES[user.role] || user.role}</span>
        <button type="button" className="rail-signout" onClick={logout}>
          <LogOut size={16} aria-hidden="true" />
          Sign out
        </button>
      </div>
    </aside>
  );
};
