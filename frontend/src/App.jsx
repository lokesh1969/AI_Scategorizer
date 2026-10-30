import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { Landing } from './pages/Landing';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Documents } from './pages/Documents';
import { DocumentDetail } from './pages/DocumentDetail';
import { Upload } from './pages/Upload';
import { VerificationQueue } from './pages/VerificationQueue';
import { Users } from './pages/Users';
import { AuditLogs } from './pages/AuditLogs';
import { Settings } from './pages/Settings';
import { Profile } from './pages/Profile';
import { REVIEWER_ROLES } from './constants';

const ProtectedLayout = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();
  const [railOpen, setRailOpen] = useState(false);

  if (loading) {
    return <div className="loading">Checking your session…</div>;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (allowedRoles && !allowedRoles.includes(user.role) && user.role !== 'ADMIN') {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className={`shell${railOpen ? ' rail-open' : ''}`}>
      <Sidebar onNavigate={() => setRailOpen(false)} />
      <div style={{ minWidth: 0 }}>
        <Navbar onMenu={() => setRailOpen(true)} />
        <main className="main" onClick={() => railOpen && setRailOpen(false)}>
          {children}
        </main>
      </div>
    </div>
  );
};

const page = (el, allowedRoles) => <ProtectedLayout allowedRoles={allowedRoles}>{el}</ProtectedLayout>;

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={page(<Dashboard />)} />
          <Route path="/documents" element={page(<Documents />)} />
          <Route path="/documents/:id" element={page(<DocumentDetail />)} />
          <Route path="/upload" element={page(<Upload />, ['ADMIN', 'UPLOADER'])} />
          <Route path="/verification" element={page(<VerificationQueue />, ['ADMIN', ...REVIEWER_ROLES])} />
          <Route path="/users" element={page(<Users />, ['ADMIN'])} />
          <Route path="/audit-logs" element={page(<AuditLogs />, ['ADMIN'])} />
          <Route path="/settings" element={page(<Settings />, ['ADMIN'])} />
          <Route path="/profile" element={page(<Profile />)} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
