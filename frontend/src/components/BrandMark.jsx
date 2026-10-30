import React from 'react';

// A destination tag seen edge-on: punched hole, string, stripe.
export const BrandMark = ({ size = 34 }) => (
  <span className="brand-mark" style={{ width: size, height: size }} aria-hidden="true">
    <svg width={size * 0.62} height={size * 0.62} viewBox="0 0 24 24" fill="none">
      <path d="M4 7.5 9.5 3H20v18H9.5L4 16.5z" fill="#14171c" />
      <circle cx="8.6" cy="12" r="1.7" fill="#facc15" />
      <path d="M13 8h4.5M13 12h4.5M13 16h4.5" stroke="#facc15" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  </span>
);
