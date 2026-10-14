# Product Requirements Document (PRD) — CineMatrix Studio

**Product Title:** CineMatrix Studio (formerly *Storyboard AI*)
**Level:** Level 3 — Oscar / World-Class Prestige  
**Author & Executive Sponsor:** Kirk LaSalle  
**Governance:** PRISM Sacred Covenant & Permanent Active Directives (The 10 Laws)  
**Version:** 3.3.0 · **Last reviewed:** 2026-10-14

> Delivery status against this PRD is tracked in [STATUS.md](./STATUS.md).

---

## 1. Executive Summary

CineMatrix Studio is an enterprise-grade generative pre-visualization and cinematic creation suite. It transforms screenplays, comic scripts, and literary works into broadcast-quality visual storyboards, synchronized multi-voice table reads, motion animatics, and 300 DPI print-ready graphic novels.

---

## 2. Core Pillars & Architecture

### 2.1 The 9 Studio Destinations

The application exposes nine navigable destinations — **six creative studios** plus three supporting workspaces — each reachable via a dedicated `1`–`9` NLE keyboard shortcut. The list below groups them by role; see [USER_GUIDE.md](./USER_GUIDE.md) §2 for the exact key mapping.

**Creative studios**

1. **Storyboard Gallery:** 16 curated visual styles, dynamic prompt tuning, camera shot specs, lightbox inspection, and the master export suite.
2. **Multimodal Animatics Studio:** Ken Burns sub-pixel camera motion synthesis, 6 camera presets, and a stitched master video reel (`.mp4`).
3. **AI Story Doctor & Beat Sheet:** Blake Snyder 15-beat structural classifier, narrative tension curve, and interactive dramaturgy chat.
4. **Virtual Table Read Studio:** Multi-voice teleprompter with speech cadence timing and line auditioning.
5. **Casting & Character Library:** Jungian archetype taxonomy, 6 voice profiles, visual-consistency look-books, 4-angle turnarounds, and 6-expression matrices.
6. **Graphic Novel Creation Studio:** Multi-panel dynamic layout engine (1–9 panels, Webtoon scroll), speech balloon placement, and a 300 DPI CMYK print PDF engine.

**Supporting workspaces**

7. **Projects Hub:** Central project workspace with telemetry metrics, multi-format ingestion, and instant deck export.
8. **Example Scripts Hub:** 27-script curated sample library with 1-click project creation.
9. **Provider Configuration:** Multi-provider setup, connectivity testing, and encrypted key storage.

Universal `.cbz` / `.cbr` / `.epub` parsing is a platform-wide ingestion capability available to every studio, not a separate destination.

---

## 3. Supported File Formats & I/O Matrix

### Ingestion Matrix
- **Final Draft:** `.fdx`
- **Fountain Screenplay:** `.fountain`, `.spmd`
- **Microsoft Word:** `.docx`
- **Adobe PDF:** `.pdf`
- **Comic Archives:** `.cbz`, `.cbr`
- **ePub Publications:** `.epub`
- **Plain Text / Prose:** `.txt`

### Export Matrix
- **16:9 Landscape Executive PDF Deck** (`/export/storyboard.pdf`)
- **Full ZIP Frame Archive** (`/export/images.zip`)
- **Master Video Animatic Reel (`.mp4`)** (`/export/animatic-reel.mp4`)
- **Comic Book Archive (`.cbz`) with `ComicInfo.xml`** (`/export/storyboard.cbz`)
- **Executive Character Look-Book PDF** (`/export/character-lookbook.pdf`)
- **300 DPI Graphic Novel Print Edition PDF** (`/export/graphic-novel-print.pdf`)
- **Production Shot List CSV** (`/export/shot-list.csv`)
- **Fountain Screenplay** (`/export/script.fountain`)

---

## 4. Non-Functional Requirements & Performance
- **Zero API Lock-in:** Full local offline fallback for camera motion synthesis, procedural audio scoring, and PDF generation.
- **Reproducible Installs:** Fully pinned runtime dependencies; the product must install and boot from a clean checkout before any release ships.
- **Verified Test Execution:** Backend suite of **117 automated tests** completing in ~15 seconds.
- **Responsive UI:** Sub-100ms UI interactions built on React 18, Tailwind CSS, and Vite, under `strict` TypeScript.
- **Local-First Security Posture:** Loopback-only binding, CORS restricted to localhost origins, encrypted provider key storage, and path-containment enforcement on all file reads.
- **Data Privacy & IP Ownership:** 100% of all generated scripts, prompts, character designs, storyboards, animatics, and graphic novels remain the exclusive intellectual property of Kirk LaSalle.

---

## 5. Open Requirements

The following PRD commitments are **not yet fully met** and are scheduled in [ROADMAP.md](./ROADMAP.md):

| Requirement | Gap | Phase |
|---|---|---|
| Encrypted key storage | Falls back to plaintext on encryption failure; fixed development secret | 11 |
| Bounded, validated ingestion | No extension allow-list or archive decompression limits | 11 |
| Responsive under load | Long renders block the event loop; no job queue | 12 |
| Verified UI quality | No frontend test coverage | 13 |
| Cross-platform desktop | Launcher is Windows-first | 14 |
