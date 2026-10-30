import React from 'react';
import { Link } from 'react-router-dom';
import { Menu } from 'lucide-react';
import { BrandMark } from './BrandMark';

// Shown only on narrow screens, where the rail slides in from the left.
export const Navbar = ({ onMenu }) => (
  <header className="topbar">
    <button type="button" className="icon-btn" onClick={onMenu} aria-label="Open navigation">
      <Menu size={22} />
    </button>
    <Link to="/" className="brand" style={{ padding: 0 }}>
      <BrandMark size={30} />
      <span className="brand-name" style={{ color: 'var(--belt-ink)', fontSize: '1.25rem' }}>AI Scategorizer</span>
    </Link>
  </header>
);
