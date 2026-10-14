# Developer Guide — CineMatrix Studio

**Governance:** PRISM Sacred Covenant & Permanent Active Directives (The 10 Laws)  
**Standard:** Level 3 — Oscar / World-Class Prestige  
**Applies to:** v3.3.0 · **Last reviewed:** 2026-10-14

> Current project state: [STATUS.md](./STATUS.md) · Full API: [API_REFERENCE.md](./API_REFERENCE.md)

---

## 0. Environment Setup

```bash
# 1. Create a virtual environment (Python 3.12+; verified on 3.14)
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# 2. Install dependencies
pip install -r backend/requirements-dev.txt   # runtime + pytest
# or, runtime only:
pip install -r backend/requirements.txt

# 3. Verify the backend boots
cd backend && python -c "import main; print(main.APP_VERSION)"

# 4. Install frontend dependencies
cd ../frontend && npm ci
```

> **Important.** `backend/requirements.txt` is fully pinned and must stay complete. `backend/main.py` imports `video_engine` (and therefore `cv2` + `numpy`) at module load time, so an incomplete requirements file makes the API fail to start, not degrade gracefully. `backend/tests/test_security_paths.py` enforces this contract.

---

## 1. System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND CLIENT (React 18 + TS + Vite)         │
│  • App.tsx (Projects Hub / Navigation Router)                          │
│  • StoryboardGallery.tsx & PresentationMode.tsx (Gallery & Pitch)     │
│  • CharacterLibraryView.tsx & TableReadStudio.tsx (Casting & Prompter)│
│  • StoryDoctorView.tsx & GraphicNovelStudio.tsx (Analysis & Comics)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / JSON / Binary Streams
┌───────────────────────────────────▼────────────────────────────────────┐
│                        BACKEND API (FastAPI + Python 3.10+)            │
│  • main.py (REST Endpoints & Static Mounting)                          │
│  • export_service.py & concept_art_engine.py (ReportLab PDF Suite)     │
│  • video_engine.py (OpenCV Ken Burns Sub-Pixel Motion Cam)             │
│  • story_doctor.py (Blake Snyder 15-Beat Classification Engine)        │
│  • graphic_novel_engine.py (Multi-Panel Layout & Speech Balloons)      │
│  • audio_scoring_engine.py (Procedural 16-Bit Stereo WAV Synthesizer)  │
│  • parsers/ (FDX, Fountain, DOCX, PDF, CBZ, CBR, EPUB)                 │
│  • database/models.py (SQLAlchemy SQLite ORM + Auto-Migrations)        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Directory Structure

```
cinematrix/
├── backend/
│   ├── database/
│   │   ├── models.py           # Database models & auto-migration engine
│   │   └── storyboard.db       # Primary SQLite database
│   ├── parsers/
│   │   ├── format_detector.py  # Extension and magic byte format sniffing
│   │   ├── fdx_parser.py       # Final Draft XML parser
│   │   ├── fountain_parser.py  # Fountain screenplay parser
│   │   ├── docx_parser.py      # Word document parser
│   │   ├── comic_parser.py     # .cbz/.cbr parser & CBZ packager
│   │   └── epub_parser.py      # .epub chapter & text extractor
│   ├── providers/              # OpenAI, Anthropic, Google GenAI, Groq, OpenRouter, Local
│   ├── tests/                  # Pytest unit & integration suite (117 tests)
│   ├── audio_scoring_engine.py # Pure Python procedural soundtrack & foley generator
│   ├── character_library.py    # Archetype taxonomy & voice profiles
│   ├── concept_art_engine.py   # Turnaround model sheets & look-book PDFs
│   ├── examples_service.py     # 27-script sample catalog + safe path resolution
│   ├── export_service.py       # 16:9 PDF decks, ZIP bundles, and CBZ exporter
│   ├── genre_vault.py          # Genre configurations & camera suggestions
│   ├── graphic_novel_engine.py # Multi-panel layout templates & print PDF
│   ├── story_doctor.py         # Blake Snyder 15-beat sheet & tension arc
│   ├── style_vault.py          # 16 visual aesthetic styles & prompt prefixes
│   ├── table_read_orchestrator.py # Dialogue cues & speech cadence timeline
│   ├── video_engine.py         # OpenCV Ken Burns camera motion animatics
│   ├── requirements.txt        # Pinned runtime dependencies
│   ├── requirements-dev.txt    # Runtime + test dependencies
│   └── main.py                 # Core FastAPI REST routes (60 endpoints)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── StoryboardGallery.tsx
│   │   │   ├── CharacterLibraryView.tsx
│   │   │   ├── TableReadStudio.tsx
│   │   │   ├── StoryDoctorView.tsx
│   │   │   ├── GraphicNovelStudio.tsx
│   │   │   ├── ExampleScriptsHub.tsx
│   │   │   ├── PresentationMode.tsx
│   │   │   ├── NleShortcutsModal.tsx
│   │   │   ├── ShutdownModal.tsx
│   │   │   ├── ScriptUploader.tsx
│   │   │   └── Configuration.tsx
│   │   ├── hooks/useNleKeyboardShortcuts.ts  # J-K-L & 1-9 studio switching
│   │   ├── App.tsx             # Main router & Projects Hub
│   │   └── utils/api.ts        # API base URL configuration
│   ├── .eslintrc.cjs
│   ├── package.json
│   └── vite.config.ts
├── docs/                       # Canonical documentation suite
│   ├── STATUS.md               # Current project status (start here)
│   ├── AUDIT_2026-10-14.md     # Full codebase & documentation audit
│   ├── CHANGELOG.md
│   ├── ROADMAP.md
│   ├── API_REFERENCE.md
│   ├── examples/               # 27 sample scripts
│   └── archive/                # Historical planning documents
├── desktop_launcher.py         # Desktop shell & process supervisor
├── build_desktop.py            # Desktop distribution builder
├── start_storyboard.bat        # Windows one-click master launcher
├── start_storyboard.ps1        # PowerShell master launcher
└── run_tests.bat               # Unified test runner
```

---

## 3. Running & Testing

### 3.1 Backend Pytest
```bash
python -m pytest backend/tests/ -v
# Expected: 117 passed in ~15s
```

### 3.2 Frontend Lint, Typecheck & Build
```bash
cd frontend
npm run lint        # ESLint — exit 0 (warnings are tracked, not fatal)
npm run lint:strict # zero-warning gate — currently 84 warnings outstanding
npm run typecheck   # tsc --noEmit, strict mode
npm run build       # Vite production bundle
```

### 3.3 Release Gate
No release ships unless all of the following pass from a **clean checkout**:
`pip install -r backend/requirements-dev.txt` → `pytest backend/tests` → `npm ci` → `npm run lint` → `npm run build`.

---

## 4. Key Architectural Patterns

### 4.1 Database Auto-Migration
Database schema migrations run automatically inside `init_db()` in `backend/database/models.py`. Any new column added to SQLite models is inspected via `PRAGMA table_info` and added with `ALTER TABLE ADD COLUMN` if not present.

### 4.2 Local Sub-Pixel Ken Burns Synthesis
`backend/video_engine.py` generates 24 FPS 1080p MP4 animatics using OpenCV affine matrix transformations with sub-pixel bicubic interpolation, smooth ease-in-out curve dampening, and automated frame padding.

### 4.3 Procedural Audio Synthesis
`backend/audio_scoring_engine.py` generates 16-bit 44.1kHz stereo PCM WAV buffers mathematically using harmonic overtones, ADSR envelopes, and LFO modulators with zero external C-dependencies.
