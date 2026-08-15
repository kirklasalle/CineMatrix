# Developer Guide — Storyboard AI

**Governance:** PRISM Sacred Covenant & Permanent Active Directives (The 10 Laws)  
**Standard:** Level 3 — Oscar / World-Class Prestige  

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
storyboard/
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
│   ├── tests/                  # Pytest unit & integration test suite (97 tests)
│   ├── audio_scoring_engine.py # Pure Python procedural soundtrack & foley generator
│   ├── character_library.py    # 14,000+ archetype taxonomy & voice profiles
│   ├── concept_art_engine.py   # Turnaround model sheets & look-book PDFs
│   ├── export_service.py       # 16:9 PDF decks, ZIP bundles, and CBZ exporter
│   ├── genre_vault.py          # 18 genre configurations & camera suggestions
│   ├── graphic_novel_engine.py # Multi-panel layout templates & print PDF
│   ├── story_doctor.py         # Blake Snyder 15-beat sheet & tension arc
│   ├── style_vault.py          # 16 visual aesthetic styles & prompt prefixes
│   ├── table_read_orchestrator.py # Dialogue cues & speech cadence timeline
│   ├── video_engine.py         # OpenCV Ken Burns camera motion animatics
│   └── main.py                 # Core FastAPI REST routes
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── StoryboardGallery.tsx
│   │   │   ├── CharacterLibraryView.tsx
│   │   │   ├── TableReadStudio.tsx
│   │   │   ├── StoryDoctorView.tsx
│   │   │   ├── GraphicNovelStudio.tsx
│   │   │   ├── PresentationMode.tsx
│   │   │   ├── ScriptUploader.tsx
│   │   │   └── Configuration.tsx
│   │   ├── App.tsx             # Main router & Projects Hub
│   │   └── utils/api.ts        # API client configuration
│   ├── package.json
│   └── vite.config.ts
├── docs/                       # Complete documentation suite
├── start_storyboard.bat        # Windows one-click master launcher
├── start_storyboard.ps1        # PowerShell master launcher
└── run_tests.bat               # Unified test runner
```

---

## 3. Running & Testing

### 3.1 Backend Pytest
```bash
python -m pytest backend/tests/ -v
# Output: 97 passed in ~2.5s (100% pass rate)
```

### 3.2 Frontend Build & Lint
```bash
cd frontend
npm run build
# Output: Vite production bundle built with 0 errors
```

---

## 4. Key Architectural Patterns

### 4.1 Database Auto-Migration
Database schema migrations run automatically inside `init_db()` in `backend/database/models.py`. Any new column added to SQLite models is inspected via `PRAGMA table_info` and added with `ALTER TABLE ADD COLUMN` if not present.

### 4.2 Local Sub-Pixel Ken Burns Synthesis
`backend/video_engine.py` generates 24 FPS 1080p MP4 animatics using OpenCV affine matrix transformations with sub-pixel bicubic interpolation, smooth ease-in-out curve dampening, and automated frame padding.

### 4.3 Procedural Audio Synthesis
`backend/audio_scoring_engine.py` generates 16-bit 44.1kHz stereo PCM WAV buffers mathematically using harmonic overtones, ADSR envelopes, and LFO modulators with zero external C-dependencies.
