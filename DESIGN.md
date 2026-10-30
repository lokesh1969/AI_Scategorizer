---
name: AI Scategorizer
description: Every document to the right desk, and the unsure ones to a person.
colors:
  concrete-ground: "#e9ebee"
  concrete-deep: "#dde0e5"
  tag-stock: "#ffffff"
  hairline: "#d3d7de"
  hairline-strong: "#b8bec8"
  ink: "#14171c"
  ink-secondary: "#444b58"
  ink-tertiary: "#5f6673"
  belt-graphite: "#14171c"
  belt-rubber: "#22262d"
  belt-ink: "#f3f4f6"
  belt-ink-secondary: "#b9bfca"
  stripe-finance: "#1d4ed8"
  stripe-hr: "#c2410c"
  stripe-legal: "#6d28d9"
  stripe-operations: "#047857"
  safety-yellow: "#facc15"
  finance-wash: "#e6edfd"
  hr-wash: "#fbebe3"
  legal-wash: "#efe8fc"
  operations-wash: "#e1f3ec"
  check-wash: "#fef6cf"
  danger: "#b42318"
  danger-wash: "#fdeceb"
typography:
  display:
    fontFamily: "'Archivo Variable', Archivo, system-ui, sans-serif"
    fontSize: "clamp(3rem, 6.2vw, 6rem)"
    fontWeight: 800
    lineHeight: 0.95
    letterSpacing: "-0.01em"
  page-title:
    fontFamily: "'Archivo Variable', Archivo, system-ui, sans-serif"
    fontSize: "2.25rem"
    fontWeight: 800
    lineHeight: 1
  tag-code:
    fontFamily: "'Archivo Variable', Archivo, system-ui, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 850
    lineHeight: 1
    letterSpacing: "0.02em"
  section-title:
    fontFamily: "'Archivo Variable', Archivo, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 750
    lineHeight: 1.2
  body:
    fontFamily: "'Archivo Variable', Archivo, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.5
  table-head:
    fontFamily: "'Archivo Variable', Archivo, system-ui, sans-serif"
    fontSize: "0.78rem"
    fontWeight: 700
    letterSpacing: "0.04em"
rounded:
  tag: "4px"
  large-tag: "6px"
spacing:
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "24px"
  xl: "40px"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.tag-stock}"
    rounded: "{rounded.tag}"
    padding: "0 18px"
    height: "42px"
  button-check:
    backgroundColor: "{colors.safety-yellow}"
    textColor: "{colors.ink}"
    rounded: "{rounded.tag}"
    padding: "0 18px"
    height: "42px"
  button-secondary:
    backgroundColor: "{colors.tag-stock}"
    textColor: "{colors.ink}"
    rounded: "{rounded.tag}"
    padding: "0 18px"
    height: "42px"
  input:
    backgroundColor: "{colors.tag-stock}"
    textColor: "{colors.ink}"
    rounded: "{rounded.tag}"
    padding: "9px 12px"
    height: "42px"
  panel:
    backgroundColor: "{colors.tag-stock}"
    rounded: "{rounded.tag}"
    padding: "24px"
  rail:
    backgroundColor: "{colors.belt-graphite}"
    textColor: "{colors.belt-ink}"
    width: "248px"
  rail-link-active:
    backgroundColor: "{colors.tag-stock}"
    textColor: "{colors.ink}"
    rounded: "{rounded.tag}"
    height: "42px"
---

# Design System: AI Scategorizer

## Overview

**Destination Tags.** A document is luggage that must reach the right desk. Every document wears a destination tag: a coloured stripe carrying a three-letter department code (FIN, HR, LEG, OPS) and the model's confidence beside it. Confident documents drop into their department's chute; unsure, empty or unreadable ones get the yellow CHK tag and wait at the manual check. The world borrows from baggage handling: white tag stock, thermal-black print, a graphite conveyor, and a safety-yellow inspection bay.

The light concrete ground is chosen for the scene: a panel watching a projector in a lit room, and office staff at desks in daylight. Colour is functional: each department owns one stripe colour everywhere it appears, and yellow means one thing only, a person needs to look.

The landing page (Persuade) lets the world carry the page: the sorter belt is the hero and the route, tag anatomy and inspection band are its chapters. The app (Operate) keeps standard web controls and a familiar rail-and-content layout; the world enters only through type, palette, density and the tag.

## Colors

### Primary
- **Ink** `#14171c`: text, primary buttons, the belt and the rail. Thermal-print black.
- **Safety yellow** `#facc15`: the manual check, and nothing else (CHK tags, the inspection band, queue counts, text selection, the brand mark).

### Secondary
- **Destination stripes**: Finance `#1d4ed8`, HR `#c2410c`, Legal `#6d28d9`, Operations `#047857`. Each has a wash (`#e6edfd`, `#fbebe3`, `#efe8fc`, `#e1f3ec`) for bins and pile slips.

### Neutral
- **Concrete ground** `#e9ebee`, **concrete deep** `#dde0e5` (hover, tracks), **tag stock** `#ffffff` (panels, tags), hairlines `#d3d7de` / `#b8bec8`, secondary ink `#444b58`, tertiary ink `#5f6673` (on white only).
- **Danger** `#b42318` with wash `#fdeceb`: critical and high priority, destructive actions, errors.

### Named Rules
- **One colour, one desk.** A department's stripe colour is used for that department only: tag codes, bins, chute mouths, top score bars.
- **Yellow means a person.** Safety yellow marks the manual check. Never use it as decoration or as a generic accent.

## Typography

One self-hosted family, **Archivo Variable** (width 62–125, weight 100–900), voiced by width:
- **Condensed (`font-stretch: 68%`)** at 800–850 weight for display headlines, page titles, tag codes, bin codes and counts.
- **Semi-condensed (84%)** for section titles, table heads and route titles.
- **Normal width** for body text and controls.

### Hierarchy
- Display: `clamp(3rem, 6.2vw, 6rem)`, 0.95 line height, balanced wrapping (landing only).
- Page title: 2.25rem condensed. Section title: 1.125rem semi-condensed 750.
- Body: 16px / 1.5 in the app; the landing page runs at 17px and 18px on screens 1700px and wider (projector sizing).
- Confidence values, counts and timestamps use tabular numerals.

### Named Rules
- **Codes are condensed and heavy.** Department codes always set in condensed 850, never in a lighter or wider voice.

## Layout

- App: graphite rail (248px) plus a content column up to 1280px, 24px gaps between panels. Under 900px the rail becomes a slide-in drawer behind a graphite top bar.
- Landing: sections up to 1280px wide (hero up to 1600px), generous vertical rhythm `clamp(64px, 10vh, 112px)`. The hero splits copy 5/12 and sorter 7/12, stacking under 1100px.
- Spacing steps used: 8, 12, 16, 24, 40px.

## Elevation & Depth

Flat by default: panels are white with a 1px hairline. Shadows appear only on objects that physically sit on something, such as tags, the sorter and the inspection cards: soft, with a vertical offset. Hover lifts buttons by 1px with the low shadow.

### Shadow Vocabulary
- `shadow-1`: `0 1px 2px rgba(20,23,28,.08), 0 2px 6px rgba(20,23,28,.06)` for hover lift.
- `shadow-2`: `0 2px 4px rgba(20,23,28,.08), 0 10px 24px rgba(20,23,28,.12)` for large tags, the sorter and the check cards.

## Shapes

Corners are tight: 4px for tags, buttons, inputs and panels, and 6px for large tags and the sorter. The only round shapes are the tag's punched hole and the route stations.

## Components

### Buttons
Primary is ink on white text, check is yellow with ink, and secondary is white with a strong hairline. All are 42px tall (34px small, 52px large), 650 weight, and lift 1px on hover.

### Chips
Status chips: **Routed by AI** (green wash), **Manual check** (solid yellow), **Checked by reviewer** (blue wash). Priority chips: Critical (solid danger), High (danger wash), Medium (ink outline), Low (muted).

### Cards / Containers
White panels with a 1px hairline and no nesting. Department bins carry a 6px top stripe in their colour; the manual-check bin has a yellow-and-black hazard top and a yellow wash.

### Inputs / Fields
White, 1px strong hairline, 4px corners, a blue focus ring at 3px and 18% opacity, and labels above the field.

### Navigation
A graphite rail with grey links; the active link becomes a white tag on the belt. The queue count is a yellow badge.

### Destination Tag (signature)
The coloured code block (FIN/HR/LEG/OPS, or yellow CHK) is joined to a white field holding the confidence. In the large size, the code block has a punched hole and the field adds the destination name and a printed barcode band. After a reviewer decides, the confidence is replaced with "Checked", because the model's score no longer describes the destination.

## Do's and Don'ts

### Do:
- Show every document's destination as a tag, in every list and header.
- Use the department's own colour wherever that department appears.
- Keep yellow for "a person needs to look".
- Use tabular numerals for confidences and counts.

### Don't:
- Don't add eyebrow labels or section numbers above headings.
- Don't use gradient text, glass or blur, or glowing halos. The previous dark neon theme is retired.
- Don't use rows of identical icon cards as page structure.
- Don't show a model confidence on a document a person has re-routed.
