import React, { forwardRef, useEffect, useImperativeHandle, useRef, useState } from 'react';

// Sample documents riding the belt. The first two are real results from a local
// test run; the rest are illustrative samples (the section is labelled as a demonstration).
const SAMPLES = [
  { file: 'vendor_invoice_march.txt', code: 'FIN', conf: 82.1 },
  { file: 'leave_request_rkumar.docx', code: 'HR', conf: 74.0 },
  { file: 'nda_acme_supplies.pdf', code: 'LEG', conf: 91.3 },
  { file: 'meeting_note.txt', code: 'CHK', conf: 56.8 },
  { file: 'warehouse_incident_0412.jpg', code: 'OPS', conf: 88.4 },
  { file: 'gst_return_sept.pdf', code: 'FIN', conf: 93.0 },
  { file: 'salary_revision_q3.xlsx', code: 'HR', conf: 79.2 },
  { file: 'scanned_letter_hindi.png', code: 'CHK', conf: 48.5 },
  { file: 'lease_renewal_notice.pdf', code: 'LEG', conf: 86.7 },
  { file: 'shift_roster_week42.xlsx', code: 'OPS', conf: 77.9 },
];

export const CHUTES = [
  { code: 'FIN', name: 'Finance' },
  { code: 'HR', name: 'HR' },
  { code: 'LEG', name: 'Legal' },
  { code: 'OPS', name: 'Operations' },
  { code: 'CHK', name: 'Manual check' },
];

const chuteIndex = (code) => CHUTES.findIndex((c) => c.code === code);
const SPAWN_MS = 1500;
const BELT_MS_PER_WIDTH = 3200; // time to cross the whole belt
const DROP_MS = 560; // fall into the chute, the same for every tag
const FLIGHT_MS = 760; // a handed-off tag lifted from the scanner onto the belt
const HIT_MS = 1100; // how long a chute stays marked after a handed-off tag lands

const reducedMotion = () =>
  typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

const initialBins = () => Object.fromEntries(CHUTES.map((c) => [c.code, []]));

// A loose copy of a parcel, flown across the page above everything else
const flyingParcel = (parcel) => {
  const el = document.createElement('div');
  el.className = `parcel parcel-${parcel.code.toLowerCase()} parcel-featured parcel-flying`;
  el.setAttribute('aria-hidden', 'true');
  const code = document.createElement('span');
  code.className = 'parcel-code';
  code.textContent = parcel.code;
  const conf = document.createElement('span');
  conf.className = 'parcel-conf num';
  conf.textContent = `${parcel.conf.toFixed(1)}%`;
  el.append(code, conf);
  return el;
};

/**
 * The belt and chutes. Spawns sample parcels on its own; a parent can also hand it a
 * parcel through ref.handOff(parcel, rect), which flies from rect onto the belt start.
 */
export const Sorter = forwardRef(({ spawnMs = SPAWN_MS }, ref) => {
  const [parcels, setParcels] = useState([]);
  const [hit, setHit] = useState(null);
  const beltRef = useRef(null);
  const [bins, setBins] = useState(() => {
    if (!reducedMotion()) return initialBins();
    // Static end state for visitors who prefer no motion
    const b = initialBins();
    SAMPLES.forEach((s) => b[s.code].push(s));
    return b;
  });
  const next = useRef(0);
  const uid = useRef(0);

  useEffect(() => {
    if (reducedMotion()) return undefined;
    const spawn = () => {
      const sample = SAMPLES[next.current % SAMPLES.length];
      next.current += 1;
      uid.current += 1;
      setParcels((p) => [...p, { ...sample, id: uid.current }]);
    };
    spawn();
    const t = setInterval(spawn, spawnMs);
    return () => clearInterval(t);
  }, [spawnMs]);

  useImperativeHandle(ref, () => ({
    handOff(parcel, from) {
      const belt = beltRef.current;
      if (!belt) return;
      const b = belt.getBoundingClientRect();
      const x0 = from.left + from.width / 2;
      const y0 = from.top + from.height / 2;
      const dx = b.left + b.width * 0.03 - x0;
      const dy = b.top + b.height / 2 - y0;
      const el = flyingParcel(parcel);
      Object.assign(el.style, { left: `${x0}px`, top: `${y0}px` });
      document.body.append(el);
      // Lift, arc over, set down at the start of the belt
      const flight = el.animate(
        [
          { transform: 'translate(-50%, -50%) scale(1.15)', offset: 0 },
          { transform: `translate(calc(-50% + ${dx * 0.5}px), calc(-50% + ${dy * 0.5 - 70}px)) scale(1.25)`, offset: 0.45 },
          { transform: `translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px)) scale(1.12)`, offset: 1 },
        ],
        { duration: FLIGHT_MS, easing: 'cubic-bezier(0.45, 0, 0.2, 1)' }
      );
      flight.onfinish = () => {
        el.remove();
        uid.current += 1;
        setParcels((p) => [...p, { ...parcel, id: uid.current, featured: true }]);
      };
    },
  }));

  const land = (parcel) => {
    setParcels((p) => p.filter((x) => x.id !== parcel.id));
    if (parcel.featured) {
      setHit({ code: parcel.code, id: parcel.id });
      setTimeout(() => setHit((h) => (h?.id === parcel.id ? null : h)), HIT_MS);
    }
    setBins((b) => {
      const pile = [parcel, ...b[parcel.code]].slice(0, 4);
      return { ...b, [parcel.code]: pile, [`${parcel.code}_n`]: (b[`${parcel.code}_n`] || 0) + 1 };
    });
  };

  return (
    <figure className="sorter" aria-label="Demonstration: sample documents being sorted into departments">
      <div ref={beltRef} className="sorter-belt" aria-hidden="true">
        <div className="sorter-slats" />
        {/* With motion turned off, two tags rest on the belt so the mechanism still reads */}
        {reducedMotion() &&
          [SAMPLES[0], SAMPLES[3]].map((p, i) => (
            <div key={p.file} className={`parcel parcel-${p.code.toLowerCase()} parcel-still`} style={{ left: `${28 + i * 34}%` }}>
              <span className="parcel-code">{p.code}</span>
              <span className="parcel-conf num">{p.conf.toFixed(1)}%</span>
            </div>
          ))}
        {parcels.map((p) => {
          const x = (chuteIndex(p.code) + 0.5) * 20;
          // Constant belt speed: ride time grows with distance, so tags never overtake
          const ride = Math.round(((x - 3) / 100) * BELT_MS_PER_WIDTH);
          return (
          <div
            key={p.id}
            className={`parcel parcel-${p.code.toLowerCase()} ${p.featured ? 'parcel-featured' : ''}`}
            style={{
              '--x': `${x}%`,
              animation: `parcel-ride ${ride}ms linear forwards, parcel-drop ${DROP_MS}ms cubic-bezier(0.55, 0, 0.9, 0.4) ${ride}ms forwards`,
            }}
            onAnimationEnd={(e) => e.animationName === 'parcel-drop' && land(p)}
          >
            <span className="parcel-code">{p.code}</span>
            <span className="parcel-conf num">{p.conf.toFixed(1)}%</span>
          </div>
          );
        })}
      </div>

      <div className="chutes">
        {CHUTES.map((c) => {
          const pile = bins[c.code] || [];
          const count = bins[`${c.code}_n`] ?? pile.length;
          return (
            <div key={c.code} className={`chute chute-${c.code.toLowerCase()} ${hit?.code === c.code ? 'is-hit' : ''}`}>
              <div className="chute-mouth" aria-hidden="true" />
              <div className="chute-label">
                <span className="chute-code">{c.code}</span>
                <span className="chute-name">{c.name}</span>
              </div>
              <div className="chute-count num" aria-label={`${count} documents`}>{count}</div>
              <ul className="chute-pile">
                {pile.map((p, i) => (
                  <li key={`${p.file}-${i}`} title={p.file} className={p.featured ? 'is-featured' : undefined}>
                    <span className="pile-file">{p.file}</span>
                    <span className="pile-conf num">{p.conf.toFixed(1)}%</span>
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>
      <figcaption className="sorter-note">
        Demonstration with sample files. Below 70% confidence, a document is held for a person.
      </figcaption>
    </figure>
  );
});
Sorter.displayName = 'Sorter';
