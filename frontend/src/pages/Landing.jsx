import React, { useCallback, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  FileUp,
  ScanText,
  Tags,
  Gauge,
  Split,
  ScrollText,
  UserCheck,
  CornerDownRight,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Sorter } from '../components/Sorter';
import { Scanner } from '../components/Scanner';
import { DestTag } from '../components/Tags';
import { BrandMark } from '../components/BrandMark';
import '../styles/landing.css';

const ROUTE = [
  {
    icon: FileUp,
    title: 'Drop it in',
    text: 'Upload a PDF, Word, Excel or text file, or a photo or scan of paper, up to 25 MB.',
  },
  {
    icon: ScanText,
    title: 'Read it',
    text: 'Digital text is read directly. Scans are cleaned up (contrast, noise, tilt) and read with OCR in English and Hindi.',
  },
  {
    icon: Tags,
    title: 'Tag it',
    text: 'A fine-tuned transformer model scores the text against Finance, HR, Legal and Operations.',
  },
  {
    icon: Gauge,
    title: 'Check the confidence',
    text: "If the top score clears the administrator's threshold (70% by default), the tag is final.",
  },
  {
    icon: Split,
    title: 'Route or hold',
    text: 'Confident documents go straight to their department. Unsure, empty or unreadable ones wait for a person.',
  },
  {
    icon: ScrollText,
    title: 'Keep the record',
    text: 'Uploads, views, reviews and setting changes are written to an audit log.',
  },
];

// Real output from a local test run of the system
const INVOICE = {
  file: 'vendor_invoice_march.txt',
  probs: [
    ['FINANCE', 'FIN', 82.1],
    ['LEGAL', 'LEG', 7.5],
    ['HR', 'HR', 5.7],
    ['OPERATIONS', 'OPS', 4.7],
  ],
  found: [
    ['Total', 'Rs. 57,230'],
    ['Date', '12 March 2026'],
    ['Invoice no.', 'INV-2291'],
  ],
  summary: [
    'Office supplies and printer cartridges for March, quantity 40 units.',
    'Payment is due within 30 days to the bank account listed below.',
    'Late payment attracts a penalty of 2% per month.',
  ],
};

const NOTE_PROBS = [
  ['HR', 'HR', 56.8],
  ['FINANCE', 'FIN', 18.2],
  ['OPERATIONS', 'OPS', 13.6],
  ['LEGAL', 'LEG', 11.4],
];

const ROLES = [
  ['Uploader', 'Their own uploads', 'Upload documents and follow what happened to them'],
  ['Finance Manager', 'Finance documents and the manual-check queue', 'Confirm or re-route documents in the queue'],
  ['HR Manager', 'HR documents and the manual-check queue', 'Confirm or re-route documents in the queue'],
  ['Legal Counsel', 'Legal documents and the manual-check queue', 'Confirm or re-route documents in the queue'],
  ['Operations Manager', 'Operations documents and the manual-check queue', 'Confirm or re-route documents in the queue'],
  ['Administrator', 'Everything', 'Manage users, set the confidence threshold, read the audit log'],
];

const STACK = [
  ['Interface', 'React and Vite'],
  ['Service', 'FastAPI (Python)'],
  ['Reading scans', 'Tesseract OCR with OpenCV clean-up'],
  ['Classifier', 'Fine-tuned transformer (Hugging Face)'],
  ['Storage', 'MongoDB, or SQLite when MongoDB is absent'],
  ['Security', 'Sign-in tokens, hashed passwords, server-side role checks'],
];

const ScoreBars = ({ rows, threshold = 70, highlight }) => (
  <div className="scorebars" role="table" aria-label="Model scores per department">
    <div className="scorebars-threshold" style={{ '--t': threshold / 100 }} aria-hidden="true">
      <span>{threshold}% threshold</span>
    </div>
    {rows.map(([cat, code, v]) => (
      <div key={cat} className="scorebar" role="row">
        <span className="scorebar-code" role="rowheader">{code}</span>
        <span className="scorebar-track" role="cell">
          <span
            className={`scorebar-fill fill-${code.toLowerCase()} ${cat === highlight ? 'is-top' : ''}`}
            style={{ width: `${v}%` }}
          />
        </span>
        <span className="scorebar-val num" role="cell">{v.toFixed(1)}%</span>
      </div>
    ))}
  </div>
);

export const Landing = () => {
  const { user } = useAuth();
  const sorterRef = useRef(null);
  // With the scanner feeding the belt on desktop, sample parcels come less often
  const [spawnMs] = useState(() => (window.matchMedia('(min-width: 1101px)').matches ? 2600 : 1500));
  const handOff = useCallback((parcel, rect) => sorterRef.current?.handOff(parcel, rect), []);
  const demoLink = user ? '/dashboard' : '/login';
  const demoText = user ? 'Open your dashboard' : 'Open the live demo';

  return (
    <div className="landing">
      <header className="lp-bar">
        <a href="#top" className="brand lp-brand" aria-label="AI Scategorizer home">
          <BrandMark />
          <span className="brand-name">AI Scategorizer</span>
        </a>
        <nav className="lp-nav" aria-label="Page sections">
          <a href="#how">How it works</a>
          <a href="#tag">Read a tag</a>
          <a href="#check">Manual check</a>
          <a href="#roles">Who sees what</a>
        </nav>
        <Link to={demoLink} className="btn btn-check btn-sm">
          {user ? 'Dashboard' : 'Sign in'}
        </Link>
      </header>

      <main id="top">
        {/* First viewport: the offer and the mechanism at work */}
        <section className="lp-hero">
          <div className="lp-hero-copy">
            <h1 className="display lp-headline">
              Sort every document.
              <span> Check the unsure ones.</span>
            </h1>
            <p className="lp-lede">
              AI Scategorizer reads incoming office documents, decides whether each belongs to Finance, HR,
              Legal or Operations, and sends it there on its own only when it is confident. Everything else waits
              for a person to check.
            </p>
            <div className="lp-actions">
              <Link to={demoLink} className="btn btn-primary btn-lg">
                {demoText}
                <ArrowRight size={18} />
              </Link>
              <a href="#how" className="btn btn-lg">See how it works</a>
            </div>
          </div>
          <div className="lp-hero-floor">
            <Scanner onHandOff={handOff} />
            <Sorter ref={sorterRef} spawnMs={spawnMs} />
          </div>
        </section>

        {/* The route a document travels */}
        <section id="how" className="lp-section">
          <div className="lp-section-head">
            <h2 className="display lp-h2">How a document travels</h2>
            <p className="lp-section-lede">
              Six stops from upload to the right desk. Each one is a real part of the system you can open in the demo.
            </p>
          </div>
          <ol className="route">
            {ROUTE.map(({ icon: Icon, title, text }) => (
              <li key={title} className="route-stop">
                <span className="route-node" aria-hidden="true">
                  <Icon size={20} />
                </span>
                <h3 className="route-title">{title}</h3>
                <p className="route-text">{text}</p>
              </li>
            ))}
          </ol>
        </section>

        {/* One real routed document, read field by field */}
        <section id="tag" className="lp-section lp-tag">
          <div className="lp-section-head">
            <h2 className="display lp-h2">Read a tag</h2>
            <p className="lp-section-lede">
              The real result for <code>{INVOICE.file}</code>, a vendor invoice uploaded during testing.
            </p>
          </div>

          <div className="tag-anatomy">
            <div className="tag-hang">
              <span className="tag-string" aria-hidden="true" />
              <DestTag category="FINANCE" confidence={82.1} status="AI VERIFIED" size="lg" sub="Sent to the Finance Manager" barcode />
            </div>

            <dl className="anatomy">
              <div className="anatomy-row">
                <dt>Where it went</dt>
                <dd>
                  <strong>Finance.</strong> The model scored Finance at 82.1%, above the 70% threshold, so it was routed
                  without waiting for anyone.
                </dd>
              </div>
              <div className="anatomy-row">
                <dt>How sure it was</dt>
                <dd>
                  <ScoreBars rows={INVOICE.probs} highlight="FINANCE" />
                </dd>
              </div>
              <div className="anatomy-row">
                <dt>What it found</dt>
                <dd className="found">
                  {INVOICE.found.map(([k, v]) => (
                    <span key={k} className="found-item">
                      <span className="found-k">{k}</span>
                      <span className="found-v num">{v}</span>
                    </span>
                  ))}
                </dd>
              </div>
              <div className="anatomy-row">
                <dt>How urgent</dt>
                <dd>
                  <span className="chip chip-high">High</span> The text mentions a late-payment <em>penalty</em>.
                </dd>
              </div>
              <div className="anatomy-row">
                <dt>In three lines</dt>
                <dd>
                  <ul className="summary">
                    {INVOICE.summary.map((s) => (
                      <li key={s}>{s}</li>
                    ))}
                  </ul>
                </dd>
              </div>
            </dl>
          </div>
        </section>

        {/* The human in the loop */}
        <section id="check" className="lp-check">
          <div className="lp-check-inner">
            <div className="lp-section-head">
              <h2 className="display lp-h2">When it isn&rsquo;t sure, a person decides</h2>
              <p className="lp-section-lede">
                A vague internal note from the same test run. Its best guess was only 56.8%, so the system refused to
                guess.
              </p>
            </div>

            <div className="check-flow">
              <div className="check-step">
                <DestTag category="HR" confidence={56.8} status="HUMAN VERIFICATION REQUIRED" size="lg" sub="Model guess: HR" />
                <ScoreBars rows={NOTE_PROBS} highlight="HR" />
              </div>

              <ol className="ledger" aria-label="Audit log for meeting_note.txt">
                <li>
                  <time className="num">22:45:19</time>
                  <span><strong>meeting_note.txt</strong> uploaded by the Document Uploader</span>
                </li>
                <li>
                  <time className="num">22:45:19</time>
                  <span>Held for manual check: 56.8% is below the 70% threshold</span>
                </li>
                <li>
                  <time className="num">22:45:42</time>
                  <span>Opened from the queue by the HR Manager</span>
                </li>
                <li className="ledger-final">
                  <time className="num">22:45:47</time>
                  <span>
                    Re-routed to <strong>Operations</strong>. The model&rsquo;s guess (HR) is kept beside the decision.
                  </span>
                </li>
              </ol>
            </div>

            <div className="check-points">
              <p><UserCheck size={18} aria-hidden="true" /> Any department reviewer can work the queue; only an administrator can change a document that was already routed.</p>
              <p><CornerDownRight size={18} aria-hidden="true" /> Because the original guess is stored, the team can see how often people overrule the model.</p>
            </div>
          </div>
        </section>

        {/* Access */}
        <section id="roles" className="lp-section">
          <div className="lp-section-head">
            <h2 className="display lp-h2">Who sees what</h2>
            <p className="lp-section-lede">
              Six roles, checked by the server on every request, not just hidden in the interface.
            </p>
          </div>
          <div className="panel table-wrap">
            <table className="table roles-table">
              <thead>
                <tr>
                  <th scope="col">Role</th>
                  <th scope="col">Sees</th>
                  <th scope="col">Can do</th>
                </tr>
              </thead>
              <tbody>
                {ROLES.map(([role, sees, can]) => (
                  <tr key={role}>
                    <th scope="row" className="cell-strong">{role}</th>
                    <td>{sees}</td>
                    <td>{can}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="stack">
            <h3 className="section-title">Under the hood</h3>
            <dl className="stack-list">
              {STACK.map(([k, v]) => (
                <div key={k}>
                  <dt>{k}</dt>
                  <dd>{v}</dd>
                </div>
              ))}
            </dl>
          </div>
        </section>

        {/* Close */}
        <section className="lp-close">
          <div className="lp-close-inner">
            <h2 className="display lp-close-title">See it sort a real document.</h2>
            <p>Every role has a demo account on the sign-in page. Upload a file, then sign in as a manager to review it.</p>
            <Link to={demoLink} className="btn btn-check btn-lg">
              {demoText}
              <ArrowRight size={18} />
            </Link>
          </div>
        </section>
      </main>

      <footer className="lp-foot">
        <span className="brand-name">AI Scategorizer</span>
        <span>Final-year B.Tech Computer Science capstone project</span>
      </footer>
    </div>
  );
};
