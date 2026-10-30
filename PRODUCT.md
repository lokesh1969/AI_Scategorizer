# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
- **Presentation audience (primary for the landing page):** a panel of faculty members and industry experts evaluating this as a final-year B.Tech Computer Science capstone project. They watch it presented live, usually on a projector or large screen, and must understand what the system does and how it works within a minute, then see it working.
- **Product users (the app):** staff of an organisation that receives mixed paperwork. Uploaders submit documents; department managers (Finance, HR, Legal, Operations) receive routed documents and review uncertain ones; an administrator manages users, settings and the audit log.

## Product Purpose
AI Scategorizer reads incoming documents (PDF, Word, Excel, text, scanned images), works out which department must act on each one (Finance, HR, Legal or Operations), and routes it there automatically only when the AI is confident. Uncertain, empty or unreadable documents go to a human verification queue instead of being guessed. Success: less manual sorting without silently misrouting important documents.

## Positioning
Confidence-gated routing with a human in the loop: the system knows when not to trust itself. Every automatic decision carries its confidence and a probability for each department; reviewer corrections are stored next to the model's original prediction, and every action is audited.

## Operating Context
Upload → text extraction (digital) or OCR with image preprocessing (scans) → language detection (English, Hindi, mixed) → transformer classification → priority score, summary, entities, sentiment → confidence check against an admin-set threshold → auto-route to the department, or the human verification queue → reviewer confirms or re-routes → audit log.

## Capabilities and Constraints
- Accepts PDF, DOCX, XLSX, TXT, PNG, JPG up to 25 MB; OCR uses Tesseract (English + Hindi).
- Four departments: FINANCE, HR, LEGAL, OPERATIONS. Six roles: Admin, Finance Manager, HR Manager, Legal Counsel, Operations Manager, Uploader. Role-based access is enforced on the server.
- Confidence threshold is configurable by the admin (default 70%).
- Priority, summary, entities and sentiment are rule-based helpers for reviewers, not trained models.
- Stack: React 19 + Vite frontend, FastAPI backend, MongoDB with SQLite fallback, Hugging Face Transformers.

## Brand Commitments
- Name: **AI Scategorizer**.
- For this presentation, the landing page explains the project and its workflow; it does not present the research paper.

## Evidence on Hand
- The working application with demo accounts for every role (see PROJECT.md §5).
- Real pipeline behaviour from a local run: a vendor invoice was classified FINANCE at 82.1% and auto-routed; a vague meeting note scored 56.8% and went to human review.
- No customers, deployments, testimonials, pricing or adoption figures exist; none may be invented.

## Product Principles
1. Automate only what the system is confident about; defer the rest to people.
2. Every decision is explainable: show the category, the confidence and the alternatives.
3. People stay in charge: reviewers can correct the AI, and the original prediction is kept.
4. Every action leaves an audit trail.

## Accessibility & Inclusion
Must stay legible on a projector in a lit room (high contrast, large type at a distance) and remain fully keyboard-usable.
