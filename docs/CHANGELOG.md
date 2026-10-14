# Changelog — CineMatrix Studio

All notable changes to **CineMatrix Studio** (formerly *Storyboard AI*) are documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and is governed by **The PRISM Sacred Covenant** and **Permanent Active Directives (The 10 Laws)** by Kirk LaSalle.

Current status is tracked in [STATUS.md](./STATUS.md). Forward plans live in [ROADMAP.md](./ROADMAP.md).

---

## [3.3.0] — 2026-10-14 — Integrity & Reliability Release

A full codebase and documentation audit ([AUDIT_2026-10-14.md](./AUDIT_2026-10-14.md)) found that **v3.2.0 could not be installed or started from a clean checkout**, and confirmed an exploitable arbitrary file read. This release fixes both, repairs the CI pipeline, and brings every document back in line with the shipped code. No new features.

### 🔴 Fixed — Release Blockers

- **Application could not start from a clean install.** `backend/requirements.txt` omitted packages that `backend/main.py` imports at module load time, so `pip install -r backend/requirements.txt` produced an API that crashed on import:
  - Added `opencv-python-headless` and `numpy` — imported by `backend/video_engine.py`, which `main.py` imports directly. Without them: `ModuleNotFoundError: No module named 'cv2'`.
  - Added `PyMuPDF` and `pypdf` — used by the PDF ingestion fallback chain in `main.py` and `examples_service.py`. The error message at `main.py:1515` told users to install PyMuPDF, a package the project never declared.
  - **Replaced `google-generativeai` with `google-genai`.** `providers/google_provider.py` uses the new Google GenAI SDK (`from google import genai`); the legacy package does not provide it, producing `ImportError: cannot import name 'genai' from 'google'` and taking down the entire API.
- **All runtime dependencies are now version-pinned** against a verified-working set (Python 3.14), making installs reproducible.
- **Added `backend/requirements-dev.txt`** so the test suite has a declared, installable dependency set.
- **Repaired the GitHub Actions CI pipeline**, which installed the incomplete requirements file and therefore could not have been passing on `main`. It now installs `requirements-dev.txt`, runs on Python 3.12, and gates on frontend lint.

### 🟠 Fixed — Security

- **Arbitrary file read via sample-script path traversal.** `POST /projects/{id}/load-example` and `POST /projects/create-with-example` joined attacker-controlled `category` and `filename` values directly onto the examples directory with no containment check. A request with `{"category": "../..", "filename": "README.md"}` returned `200 OK` and ingested the out-of-tree file as project content.
  - Added `resolve_example_path()` in `backend/examples_service.py`, enforcing real-path containment within `EXAMPLES_BASE_DIR` and rejecting absolute paths, drive letters, and traversal sequences.
  - Both body-driven routes and `read_example_content()` now resolve through it; rejected paths return `400 Bad Request` and are logged as security events.
  - Verified: the previously successful exploit now returns `400 {"detail":"Invalid example script path."}`.

### 🛠️ Fixed — Tooling & Consistency

- **Restored frontend lint.** `package.json` declared a `lint` script but no ESLint configuration existed anywhere in `frontend/`, so `npm run lint` failed with *"ESLint couldn't find a configuration file"*. Added `frontend/.eslintrc.cjs` (TypeScript + React Hooks + React Refresh) and configured `no-constant-condition` to permit the SSE read loop.
- **Added `typecheck` and `lint:strict` npm scripts.** `lint` now reports warnings without failing the build; `lint:strict` retains the zero-warning gate as the Phase 13 target.
- **Single-sourced the API version.** `FastAPI(version=...)` advertised `2.0.0` while `/health` and `/` reported `3.2.0`. All three now derive from `APP_VERSION` in `backend/main.py`, and the OpenAPI title is corrected from "Storyboard AI API" to "CineMatrix Studio API".
- Aligned `frontend/package.json` to `3.3.0`.

### ✅ Added — Tests

- New `backend/tests/test_security_paths.py` (13 tests) covering:
  - path-traversal rejection across resolver, `load-example`, and `create-with-example`;
  - absolute-path and drive-letter rejection;
  - the dependency contract (required packages declared, legacy Google SDK absent);
  - version consistency across OpenAPI, `/health`, `/`, and the desktop build manifest.
- Suite total: **104 → 117 tests, all passing.**

### 📚 Documentation

- **Added [`docs/STATUS.md`](./STATUS.md)** — the single source of truth for current project state, health dashboard, known limitations, release-readiness gates, and next actions.
- **Added [`docs/AUDIT_2026-10-14.md`](./AUDIT_2026-10-14.md)** — full audit findings with file:line evidence, verified metrics, revised scoring, and the phased remediation plan.
- **Rewrote [`docs/ROADMAP.md`](./ROADMAP.md)** — now records actual delivered state alongside remediation Phases 11–14, replacing the aspirational-only plan.
- **Rewrote [`docs/API_REFERENCE.md`](./API_REFERENCE.md)** — previously documented 31 of 60 endpoints and listed `POST /projects/upload`, which does not exist. Now covers **all 60 routes** with correct paths.
- **Rebranded remaining "Storyboard AI" references** to CineMatrix Studio across the changelog, roadmap, PRD, API reference, user guide, developer guide, and the examples catalog.
- **De-duplicated documentation.** `PRD.md`, `USER_GUIDE.md`, and `DEVELOPER_GUIDE.md` existed as byte-identical copies in both the repository root and `docs/`. `docs/` is now canonical; the root copies are pointer stubs.
- **Corrected false claims** in the PRD, README, and guides: test counts, studio/workspace counts and their keyboard-shortcut order, the `14,000+ archetype combinations` figure, and the broken `d:/Projects/storyboard/...` cross-reference.
- **Rewrote [`SECURITY.md`](../SECURITY.md)** with the explicit local-first deployment model, the loopback-only warning, and the `STORYBOARD_SECRET_KEY` guidance.
- **Archived** five superseded documents into [`docs/archive/`](./archive/) with an index explaining what supersedes each.
- **Single-sourced the desktop release version.** `build_desktop.py` no longer hardcodes `3.2.0`; it reads `APP_VERSION` from `backend/main.py`, and a test prevents the hardcode from returning.

### 📦 Previously Shipped, Now Documented

These changes landed after the 3.2.0 entry was written and had never been recorded in the changelog:

- **Desktop launcher** (`desktop_launcher.py`, `build_desktop.py`, `dist_release/`) — packaged one-click startup with backend health probing and native window shell.
- **NLE keyboard navigation** — J-K-L scrubbing, 1–9 studio switcher, and Spacebar audition via `frontend/src/hooks/useNleKeyboardShortcuts.ts`, with an in-app reference modal (`NleShortcutsModal.tsx`).
- **Screenwriter Onboarding Guide** (`SCREENWRITER_ONBOARDING_GUIDE.md`).
- **GitHub community suite** — CI workflows, issue forms, pull request template, contributing guide, code of conduct, security policy, citation metadata, and licence.

---

## [3.2.0] — 2026-08-14 — World-Class Sample Scripts, Auto-Imaging & Graceful Teardown


### 🌟 Major Additions
- **27 World-Class Sample Screenplay Library (`docs/examples/`)**:
  - Organized across 4 curated categories:
    1. **Universal Formats (9 scripts)**: Final Draft `.fdx`, standard `.fountain`, Microsoft Word `.docx`, shooting `.pdf`, comic archive `.cbz`, manga archive `.cbr`, ePub podcast `.epub`, commercial spec `.txt`, 30-min sitcom teleplay `.fountain`.
    2. **Engine Showcases (6 scripts)**: Blake Snyder 15-Beat Sheet, Multi-Voice Table Read, 24 FPS Chase Animatic, Manga Split Graphic Novel, 44.1kHz Audio Score & Foley, 8 Jungian Archetypes Look-Book.
    3. **Genres & Visual Styles (9 scripts)**: Cyberpunk Neo-Noir, Historical 35mm Drama, Grimdark Psychological Horror, Military Action Blockbuster, Sunlit Romantic Comedy, Urban Fantasy Inks, Cinema Vérité Documentary, Studio Ghibli Anime Fairytale, Sergio Leone Spaghetti Western.
    4. **Duration Spectrum Tiers (3 scripts)**: 1-Minute Micro Scene, 5-Minute Short Film, 15-Minute Feature Act One.
  - Built **Interactive Example Scripts Hub** in the UI with instant 1-click project creation, script previews, and category filtering.
  - Added REST API endpoints: `GET /examples`, `GET /examples/{cat}/{filename}`, `POST /projects/create-with-example`, `POST /projects/{id}/load-example`.

- **Auto-Action Image Generation & Pre-Visualization**:
  - Automatically synthesizes and embeds 16:9 cinematic storyboard visuals whenever an example script is loaded or analyzed.
  - Implemented SSE streamed frame image persistence in SQLite and real-time gallery delivery.
  - Added deterministic high-fidelity fallback rendering so exploration never halts on unconfigured API keys.
  - Added master toolbar batch actions: **"Render All Frames"** (`POST /projects/{id}/generate-all-images`) and **"Animate All Frames"** (`POST /projects/{id}/generate-all-animatics`).

- **Cinematography Specification Bar & Lightbox Inspection**:
  - Redesigned storyboard frame cards to feature a permanent, non-overlapping **Camera & Lighting Spec Bar** displaying Shot Type, Camera Motion, Lens, Lighting, and Director's Notes with zero clipping.
  - Elevated tooltip z-index to `z-[99999]` with backdrop blur.
  - Built Fullscreen Image Lightbox Modal for high-resolution inspection of cinematography frames.

- **Graceful Studio Shutdown System**:
  - Added `POST /shutdown` endpoint with PRISM audit logging, thread safety, and scheduled OS process exit.
  - Built modal dialog confirmation with visual countdown and disconnected state in `frontend/src/components/ShutdownModal.tsx`.
  - Added global top navigation bar button with instant access.

- **Automated Verification**:
  - Expanded backend test suite to **104 automated tests (100% passing)** in `11.33s`.

---

## [3.0.0] — 2026-08-14 — Oscar / Level 3 World-Class Prestige Release

### 🚀 Major Studio Additions
- **Phase 4: Multimodal Animatics & Motion Clips**
  - Built pure local OpenCV sub-pixel affine camera motion engine in `backend/video_engine.py`.
  - Added 6 cinematic motion presets: *Dolly In*, *Dolly Out*, *Pan Left*, *Pan Right*, *Handheld Tension*, and *Slow-Mo Drift*.
  - Built Master Video Reel compiler (`.mp4`) with director title card and lower-third slates.
  - Interactive HD Video Player Modal with loop, playback controls, and direct download.
- **Phase 5: AI Story Doctor & Beat Sheet Analyzer**
  - Implemented Blake Snyder 15-Beat Sheet screenplay classifier in `backend/story_doctor.py`.
  - Real-time narrative tension curve & pacing time-series graph.
  - Interactive Story Doctor chat assistant for scene punch-ups and structural revisions.
  - Executive studio coverage analysis generator (`/projects/{id}/analysis/coverage`).
- **Phase 6: Universal Comic & ePub Parsers**
  - Added `.cbz` and `.cbr` comic book archive parser with `ComicInfo.xml` ingestion.
  - Added `.epub` digital book parser with chapter and dialogue partitioner.
  - Added standard `.cbz` comic book archive exporter.
- **Phase 7: Virtual Table Read Studio**
  - Multi-character synchronized dialogue teleprompter with auto-scrolling line highlighting.
  - Cadence speech timing model (~150 WPM) with natural conversational pauses.
  - Live line voice auditioning across 6 OpenAI TTS voice profiles.
- **Phase 8: Character Concept Art Studio & Model Sheets**
  - 4-angle turnaround model sheet generator (Front, 3/4, Profile, Back).
  - 6-expression model sheet matrix generator.
  - Executive Casting & Character Look-Book PDF deck exporter (`/export/character-lookbook.pdf`).
- **Phase 9: The Graphic Novel Creation Studio**
  - Multi-panel dynamic layout engine: 1-Splash, 2-Cinematic, 3-Strip, 4-Quadrant, 6-Grid Manga, 9-Panel Watchmen, and Webtoon scroll.
  - Geometry-aware speech balloon and caption box placement algorithm.
  - 300 DPI CMYK-ready Graphic Novel Print PDF engine.

### 🎵 Audio & Presentation Enhancements
- **Procedural Cinematic Scoring & Foley Engine (Enhancement B):**
  - 16-bit 44.1kHz stereo WAV procedural synthesizer (`backend/audio_scoring_engine.py`).
  - 6 soundtrack presets: *Cinematic Epic*, *Noir Melancholy*, *Synthwave Thriller*, *Orchestral Drama*, *Horror Drone*, *Tactical Action*.
  - 5 foley SFX presets: *Thunderstorm*, *Gunshot Reverb*, *Footsteps*, *Iron Door Creak*, *Cinematic Braam*.
- **Director Pitch & Presentation Mode (Enhancement A):**
  - Fullscreen theater mode (`frontend/src/components/PresentationMode.tsx`).
  - Keyboard navigation (`Space`, `Arrows`, `F` fullscreen, `N` notes, `Esc` exit).
  - Bottom scene thumbnail scrubber bar.

### 🛠️ Launchers & Developer Tooling
- Added `start_storyboard.bat` one-click desktop launcher for Windows.
- Added `start_storyboard.ps1` PowerShell desktop launcher.
- Added `run_tests.bat` complete test runner.

---

## [2.0.0] — 2026-08-14 — Master Presentation Export Suite & Casting

### Added
- **16:9 Landscape PDF Presentation Deck:** Full-bleed cinematic slide deck with shot types, camera framing, director notes, and intensity indicators.
- **Full ZIP Frame Archive:** Bulk exporter packaging all rendered frames into `/frames/` with CSV metadata index.
- **Projects Hub Dashboard:** Central workspace managing saved projects, telemetry counters, script formats, and one-click actions.
- **Voice Audition Player:** Interactive HTML5 audio player supporting 6 vocal profiles (`alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`).
- **Injected Character Look-Books:** Visual consistency prompts injected into frame generation pipeline.

### Fixed
- Standardized canonical `ImageGenerationError` across all AI providers.
- Added missing logger imports in `local_provider.py`.
- Fixed intensity score calculation in gallery UI (`Math.round(score * 10)%`).

---

## [1.0.0] — 2026-08-10 — Initial Release

### Added
- Core multi-format screenplay ingestion (`.fdx`, `.fountain`, `.docx`, `.pdf`, `.txt`).
- 16-Style Master Visual Style Vault (Oscar Prestige, Cyberpunk, Nordic Noir, Vintage Noir, Anime, etc.).
- Multi-provider AI generation engine (OpenAI DALL-E, Google Imagen, Anthropic Claude, Groq, Local SD).
- SQLite database persistence with automated schema migrations.
- React/TypeScript/Tailwind/Vite frontend UI.
