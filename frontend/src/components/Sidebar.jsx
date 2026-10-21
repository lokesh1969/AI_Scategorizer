import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ALL_ROLES, REVIEWER_ROLES } from '../constants';
import { 
  LayoutDashboard, 
  FileText, 
  Upload, 
  CheckCircle2, 
  Users, 
  History, 
  Settings, 
  User 
} from 'lucide-react';

export const Sidebar = () => {
  const { user } = useAuth();
  if (!user) return null;

  const role = user.role;

  const allNavItems = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, roles: ALL_ROLES },
    { label: 'Documents', path: '/documents', icon: FileText, roles: ALL_ROLES },
    { label: 'Upload', path: '/upload', icon: Upload, roles: ['ADMIN', 'UPLOADER'] },
    { label: 'Human Verification', path: '/verification', icon: CheckCircle2, roles: ['ADMIN', ...REVIEWER_ROLES] },
    { label: 'User Management', path: '/users', icon: Users, roles: ['ADMIN'] },
    { label: 'Audit Logs', path: '/audit-logs', icon: History, roles: ['ADMIN'] },
    { label: 'System Settings', path: '/settings', icon: Settings, roles: ['ADMIN'] },
    { label: 'My Profile', path: '/profile', icon: User, roles: ALL_ROLES },
  ];

  const filteredItems = allNavItems.filter(item => item.roles.includes(role));

  return (
    <aside style={{
      width: '240px',
      background: 'rgba(15, 23, 42, 0.75)',
      backdropFilter: 'blur(16px)',
      borderRight: '1px solid rgba(255, 255, 255, 0.08)',
      minHeight: 'calc(100vh - 64px)',
      padding: '24px 16px',
      display: 'flex',
      flexDirection: 'column',
      gap: '8px'
    }}>
      <div style={{ padding: '0 12px 12px 12px', fontSize: '0.7rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        Navigation
      </div>

      {filteredItems.map((item) => {
        const Icon = item.icon;
        return (
          <NavLink
            key={item.path}
            to={item.path}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '10px 14px',
              borderRadius: '8px',
              fontSize: '0.875rem',
              fontWeight: isActive ? 600 : 400,
              color: isActive ? '#06b6d4' : '#94a3b8',
              background: isActive ? 'rgba(6, 182, 212, 0.12)' : 'transparent',
              border: isActive ? '1px solid rgba(6, 182, 212, 0.25)' : '1px solid transparent',
              textDecoration: 'none',
              transition: 'all 0.2s ease'
            })}
          >
            <Icon size={18} />
            <span>{item.label}</span>
          </NavLink>
        );
      })}
    </aside>
  );
};
