import React, { useEffect, useRef, useState } from 'react';
import { DestTag } from './Tags';

// Two documents from a local test run. The invoice text follows the real file;
// the meeting note is abbreviated (the station is labelled as a demonstration).
// Each line is a list of [text, department] segments; a department marks a deciding word.
const DOCS = [
  {
    file: 'vendor_invoice_march.txt',
    category: 'FINANCE',
    scores: [['FINANCE', 'FIN', 82.1], ['LEGAL', 'LEG', 7.5], ['HR', 'HR', 5.7], ['OPERATIONS', 'OPS', 4.7]],
    readAs: 'Digital text',
    lang: 'English',
    title: [['TAX ', null], ['INVOICE', 'fin']],
    lines: [
      [['Invoice no. INV-2291', null]],
      [['Date: 12 March 2026', null]],
      [['Office supplies and printer cartridges, 40 units', null]],
      [['Total ', null], ['Rs. 57,230', 'fin']],
      [['Payment', 'fin'], [' is due within 30 days to the', null]],
      [['bank account', 'fin'], [' listed below.', null]],
      [['Late payment attracts a ', null], ['penalty', 'leg'], [' of 2% per month.', null]],
    ],
  },
  {
    file: 'meeting_note.txt',
    category: 'HR',
    scores: [['HR', 'HR', 56.8], ['FINANCE', 'FIN', 18.2], ['OPERATIONS', 'OPS', 13.6], ['LEGAL', 'LEG', 11.4]],
    readAs: 'Digital text',
    lang: 'English',
    title: [['Notes from Tuesday sync', null]],
    lines: [
      [['Discussed the ', null], ['team', 'hr'], [' plan for next quarter.', null]],
      [['Some follow-up needed on ', null], ['schedules', 'ops'], ['.', null]],
      [['Check the ', null], ['budget', 'fin'], [' before the next round.', null]],
      [['Will circle back with ', null], ['staff', 'hr'], ['.', null]],
      [['No owner assigned yet.', null]],
    ],
  },
];

const FEED_MS = 700;
const SCAN_MS = 2400;
const SCORE_MS = 1300;
const HOLD_MS = 2600;
const EXIT_MS = 500;
const CYCLE_MS = FEED_MS + SCAN_MS + SCORE_MS + HOLD_MS + EXIT_MS;
const THRESHOLD = 70;

const DEPT_NAMES = { FINANCE: 'Finance', HR: 'HR', LEGAL: 'Legal', OPERATIONS: 'Operations' };
const DEPT_CODES = { FINANCE: 'FIN', HR: 'HR', LEGAL: 'LEG', OPERATIONS: 'OPS' };
const easeOut = (t) => 1 - (1 - t) ** 3;

// Scores race up together from zero while the phase is "score"
const useRace = (running, done) => {
  const [p, setP] = useState(0);
  useEffect(() => {
    if (!running) return undefined;
    let raf;
    const start = performance.now();
    const tick = (t) => {
      const k = Math.min(1, (t - start) / SCORE_MS);
      setP(easeOut(k));
      if (k < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(raf);
      setP(0); // the next race starts from empty bars
    };
  }, [running]);
  // Outside the race the bars sit empty (before) or full (after)
  if (!running) return done ? 1 : 0;
  return p;
};

const reducedMotion = () =>
  typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

const Line = ({ segments, at, className }) => (
  <p className={className} style={{ '--at': at }}>
    {segments.map(([text, dept], i) =>
      dept ? (
        <mark key={i} className={`scan-hit hit-${dept}`}>{text}</mark>
      ) : (
        <span key={i}>{text}</span>
      )
    )}
  </p>
);

// The printed tag as a belt parcel: routed to its desk, or to the manual check
const toParcel = (doc) => {
  const conf = doc.scores[0][2];
  return { file: doc.file, conf, code: conf >= THRESHOLD ? DEPT_CODES[doc.category] : 'CHK' };
};

/**
 * Reads one document at a time. When a result is ready it hands the printed tag on
 * through onHandOff(parcel, rect), where rect is the tag's place on screen.
 */
export const Scanner = ({ onHandOff }) => {
  const still = reducedMotion();
  const [cycle, setCycle] = useState(0);
  const [phase, setPhase] = useState(still ? 'read' : 'feed');
  const tagRef = useRef(null);
  const handOff = useRef(onHandOff);
  useEffect(() => {
    handOff.current = onHandOff;
  }, [onHandOff]);

  // One timeline per document: feed in, scan, hold the result, slide out
  useEffect(() => {
    if (still) return undefined;
    const timers = [
      setTimeout(() => setPhase('scan'), FEED_MS),
      setTimeout(() => setPhase('score'), FEED_MS + SCAN_MS),
      setTimeout(() => setPhase('read'), FEED_MS + SCAN_MS + SCORE_MS),
      setTimeout(() => {
        const rect = tagRef.current?.getBoundingClientRect();
        // Hidden on small screens: nothing to hand on
        if (rect?.width) handOff.current?.(toParcel(DOCS[cycle % DOCS.length]), rect);
        setPhase('exit');
      }, CYCLE_MS - EXIT_MS),
      setTimeout(() => {
        setPhase('feed');
        setCycle((c) => c + 1);
      }, CYCLE_MS),
    ];
    return () => timers.forEach(clearTimeout);
  }, [cycle, still]);

  const doc = DOCS[cycle % DOCS.length];
  const rows = [doc.title, ...doc.lines];
  // Each deciding word, with the point in the scan where the beam reaches its line
  const hits = rows.flatMap((segments, i) =>
    segments.filter(([, d]) => d).map(([text, d]) => [text, d, (i + 0.5) / rows.length])
  );

  const settled = phase === 'read' || phase === 'exit';
  const race = useRace(phase === 'score', settled);
  const top = doc.scores[0][2];
  const routed = top >= THRESHOLD;

  return (
    <figure
      className={`scan is-${phase}`}
      style={{ '--scan-ms': `${SCAN_MS}ms`, '--feed-ms': `${FEED_MS}ms` }}
      aria-label={`Demonstration: the scanner reading ${doc.file}`}
    >
      <div className="scan-bed">
        <span className="scan-head" aria-hidden="true">
          <span className="scan-head-slot" />
        </span>
        <article key={cycle} className="scan-doc">
          <span className="scan-doc-file">{doc.file}</span>
          {rows.map((segments, i) => (
            <Line
              key={i}
              segments={segments}
              at={(i + 0.5) / rows.length}
              className={i === 0 ? 'scan-doc-title' : 'scan-doc-line'}
            />
          ))}
          <span className="scan-beam" aria-hidden="true" />
        </article>
      </div>

      <div className="scan-readout">
        <dl className="scan-facts">
          <div>
            <dt>Read as</dt>
            <dd>{doc.readAs}</dd>
          </div>
          <div>
            <dt>Language</dt>
            <dd>{doc.lang}</dd>
          </div>
        </dl>
        <div className="scan-words">
          <span className="scan-words-label">Words it weighed</span>
          <ul key={cycle}>
            {hits.map(([text, dept, at], i) => (
              <li key={`${text}-${i}`} className={`hit-${dept}`} style={{ '--at': at }}>
                {text}
              </li>
            ))}
          </ul>
        </div>

        <div className="scan-scores" role="table" aria-label="Model scores per department">
          <span className="scan-threshold" style={{ '--t': THRESHOLD / 100 }} aria-hidden="true">
            <span>{THRESHOLD}%</span>
          </span>
          {doc.scores.map(([cat, code, v], i) => (
            <div key={cat} className={`scan-score ${i === 0 ? 'is-top' : ''} hit-${code.toLowerCase()}`} role="row">
              <span className="scan-score-code" role="rowheader">{code}</span>
              <span className="scan-score-track" role="cell">
                <span className="scan-score-fill" style={{ width: `${v * race}%` }} />
              </span>
              <span className="scan-score-val num" role="cell">{(v * race).toFixed(1)}%</span>
            </div>
          ))}
        </div>

        <div className={`scan-print ${routed ? 'is-routed' : 'is-held'}`}>
          <span className="scan-print-slot" aria-hidden="true" />
          <div ref={tagRef} className="scan-print-tag">
            <DestTag
              category={doc.category}
              confidence={top}
              status={routed ? 'AI VERIFIED' : 'HUMAN VERIFICATION REQUIRED'}
              size="lg"
              sub={routed ? `Routed to ${DEPT_NAMES[doc.category]}` : 'Held for a person'}
            />
          </div>
        </div>
      </div>
    </figure>
  );
};
