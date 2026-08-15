# Changelog — Storyboard AI

All notable changes to **Storyboard AI** are documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and is governed by **The PRISM Sacred Covenant** and **Permanent Active Directives (The 10 Laws)** by Kirk LaSalle.

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
