# Storyboard AI — Advanced Implementation Roadmap (Phases 4 – 9)

> **ARCHIVED — historical document.** This roadmap predates the CineMatrix rebrand and has been superseded by [../ROADMAP.md](../ROADMAP.md). It is retained for provenance only; do not plan work from it.


**Author:** Kirk LaSalle  
**Governance Framework:** PRISM Sacred Covenant & Permanent Active Directives (The 10 Laws)  
**Standard:** Level 3 — Oscar / World-Class Prestige  

---

## 🌟 Executive Vision

Storyboard AI evolves from an industry-leading screenplay storyboarding suite into a **Universal Visual Storytelling & Production Studio**. This roadmap defines the architectural blueprints, data models, API endpoints, UX workflows, and milestone deliverables for the next six major development phases.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                          STORYBOARD AI — ADVANCED PRODUCTION SUITE                          │
├──────────────────────────┬──────────────────────────┬───────────────────────────────────────┤
│ Phase 4: Multimodal      │ Phase 5: AI Story Doctor │ Phase 6: Universal Comic              │
│ Animatics & Video Clips  │ & Beat Sheet Analyzer    │ & ePub Publication Parsers            │
├──────────────────────────┼──────────────────────────┼───────────────────────────────────────┤
│ • Runway / Luma / Kling  │ • Blake Snyder 15 Beats  │ • .cbz / .cbr Comic Archives          │
│ • Camera Motion Presets  │ • Tension & Arc Curves   │ • .epub Chapter & Dialogue Extraction │
│ • 16:9 Looping Previews  │ • Story Doctor Chatbot   │ • Panel-by-Panel Extraction           │
│ • Master Video Reel MP4  │ • Industry Coverage PDF  │ • Round-Trip Comic Exporter           │
├──────────────────────────┼──────────────────────────┼───────────────────────────────────────┤
│ Phase 7: Virtual Table   │ Phase 8: Character       │ Phase 9: The Graphic Novel            │
│ Read Studio              │ Concept Art Studio       │ Creation Studio                       │
├──────────────────────────┼──────────────────────────┼───────────────────────────────────────┤
│ • Full-Script Multi-Voice│ • Model Sheet Generator  │ • Multi-Panel Page Layout Engine      │
│ • Auto-Scrolling Reader  │ • Expression Matrices    │ • Smart Dialogue Balloon Placement    │
│ • Pacing & Cadence Engine│ • Wardrobe & Era Variants│ • Letterer Typography & SFX Graphics  │
│ • Full Table Read MP3/Stem│ • Seed Reference Locking│ • Print PDF & Webtoon Exporter        │
└──────────────────────────┴──────────────────────────┴───────────────────────────────────────┘
```

---

## 🎬 Phase 4: Multimodal Animatics & Motion Clips

### 1. Objective & Capabilities
Transform static 16:9 visual frames into 3–5 second cinematic motion animatics. Directors can simulate camera moves (dolly-in, tracking, crane, slow motion) to evaluate visual rhythm and scene choreography before physical production.

### 2. Architecture & Engine Design
- **New Engine Module:** `backend/video_engine.py` & `backend/providers/video_provider.py`
- **Supported Video Drivers:**
  - **Cloud:** Runway Gen-3 Alpha, Luma Dream Machine, Kling AI, Minimax Hailuo Video.
  - **Local:** Stable Video Diffusion (SVD) / AnimateDiff via ComfyUI WebSocket or Ollama endpoint.
- **Camera Motion Prompts:**
  - `Dolly In / Push`: "Subtle, cinematic slow camera push towards character's eyes."
  - `Lateral Tracking`: "Smooth horizontal tracking shot maintaining subject framing."
  - `Handheld Tension`: "Subtle organic handheld camera micro-shake with rack focus."
  - `Crane / Boom`: "Slow vertical crane descent revealing the background environment."

### 3. Database Schema Extensions
```python
# StoryboardFrame Model Additions:
video_path = Column(String, nullable=True)          # Local path or cloud URL
video_duration = Column(Float, default=4.0)         # Duration in seconds
motion_preset = Column(String, default="subtle")   # push, pull, pan_left, pan_right, handheld
video_status = Column(String, default="none")       # none, generating, ready, failed
```

### 4. API Endpoints
- `POST /frames/{frame_id}/generate-animatic` — Triggers video generation for a specific frame.
- `GET /frames/{frame_id}/animatic-status` — Polling / SSE progress for video generation.
- `GET /projects/{project_id}/export/animatic-reel.mp4` — Concatenates all frame videos with transition title cards using `ffmpeg-python`.

### 5. Frontend UX Deliverables
- **Gallery Integration:** "Generate Animatic" button on frame cards with motion preset dropdown.
- **Interactive Video Modal:** Frame video player with full-screen playback and speed controls.
- **Export Action:** "Export Complete Animatic Reel (.mp4)" in Master Export Suite.

---

## 🧠 Phase 5: AI Story Doctor & Beat Sheet Analyzer

### 1. Objective & Capabilities
Provide comprehensive narrative intelligence evaluating dramatic pacing, character arcs, and structural integrity using the industry-standard Blake Snyder *Save the Cat!* 15-beat methodology and Three-Act structure.

### 2. Analytical Engine
- **Module:** `backend/story_doctor.py`
- **15-Beat Classification:**
  1. *Opening Image* | 2. *Theme Stated* | 3. *Set-up* | 4. *Catalyst* | 5. *Debate*
  6. *Break into Two* | 7. *B Story* | 8. *Fun and Games* | 9. *Midpoint*
  10. *Bad Guys Close In* | 11. *All Hope is Lost* | 12. *Dark Night of the Soul*
  13. *Break into Three* | 14. *Finale* | 15. *Final Image*
- **Pacing Metrics:** Scene duration, dialogue-to-action ratio, emotional volatility score, character conflict index.

### 3. API Endpoints
- `POST /projects/{project_id}/analysis/beat-sheet` — Generates 15-beat breakdown for the screenplay.
- `GET /projects/{project_id}/analysis/narrative-arc` — Returns time-series JSON array of tension scores across scenes.
- `POST /projects/{project_id}/analysis/story-doctor/chat` — Context-aware chat assistant for dialogue punch-ups, alternative endings, and subtext polish.
- `GET /projects/{project_id}/export/story-coverage.pdf` — Oscar-grade executive studio coverage report.

### 4. Frontend UX Deliverables
- **New View:** `frontend/src/components/StoryDoctorView.tsx`
- **Interactive Pacing Chart:** SVG / Canvas line chart plotting intensity and beat milestones.
- **Side-by-Side Beat Inspector:** Click any beat to jump directly to corresponding screenplay scenes and storyboard frames.

---

## 📚 Phase 6: Universal Comic & Digital Publication Parsers

### 1. Objective & Capabilities
Expand input and output interoperability to graphic novel and digital publishing formats: `.cbz`, `.cbr`, `.epub`, and `.mobi`.

### 2. Architecture & Ingestion Pipeline
- **Module:** `backend/parsers/comic_parser.py` & `backend/parsers/epub_parser.py`
- **Ingestion Capabilities:**
  - `.epub`: Uses `ebooklib` + `beautifulsoup4` to extract chapter divisions, character dialogue, and inline artwork.
  - `.cbz` / `.cbr`: Decompresses ZIP / RAR archives, reads `ComicInfo.xml` metadata (writer, penciller, issue number), and runs OCR + panel segmentation.
- **Round-Trip Exporter:**
  - Packages rendered storyboard frames and character profiles into a compliant `.cbz` archive with auto-generated `ComicInfo.xml`.

### 3. API Endpoints
- `POST /upload` (Enhanced): Auto-detects `.cbz`, `.cbr`, and `.epub` magic bytes.
- `GET /projects/{project_id}/export/storyboard.cbz` — Downloads compressed comic package.

---

## 🎙️ Phase 7: Virtual Table Read Studio

### 1. Objective & Capabilities
Full-script virtual table read orchestrator. Automatically voices every character with their assigned OpenAI TTS voice profile, orchestrates narrator scene descriptions, adds dramatic pauses, and synchronizes audio playback with a live screenplay teleprompter.

### 2. Audio Orchestration Engine
- **Module:** `backend/table_read_orchestrator.py`
- **Capabilities:**
  - Line-by-line dialogue parsing and voice cue routing.
  - Audio stitching via `pydub` / `scipy` with adjustable inter-character pauses (default 350ms).
  - Background narrator stem generation for action blocks.
- **Database Model Additions:**
  - `SceneAudioStem` table linking scene number, timestamp, character cues, and audio file path.

### 3. API Endpoints
- `POST /projects/{project_id}/readthrough/scene/{scene_number}/generate` — Generates complete multi-character scene audio.
- `POST /projects/{project_id}/readthrough/full-script/start` — Async batch job generating full script table read.
- `GET /projects/{project_id}/readthrough/status` — Live batch generation progress.
- `GET /projects/{project_id}/export/table-read.mp3` — Single concatenated table read audio file.

### 4. Frontend UX Deliverables
- **New View:** `frontend/src/components/TableReadStudio.tsx`
- **Teleprompter Interface:** Auto-scrolls script lines in sync with audio playback.
- **Master Audio Console:** Play, pause, skip scene, scrub bar, voice volume balance sliders, and speed toggle (1.0x, 1.25x, 1.5x).

---

## 🖼️ Phase 8: Character Concept Art Studio & Model Sheets

### 1. Objective & Capabilities
Dedicated character design studio allowing directors to develop, refine, and lock character visual identities before generating full storyboards.

### 2. Generative Model Sheet Engine
- **Module:** `backend/concept_art_engine.py`
- **Generation Types:**
  - **Full-Body Portrait:** Cinematic head-to-toe hero costume render.
  - **Facial Expression Sheet:** 6-panel expression matrix (Neutral, Joy, Anger, Fear, Sorrow, Intense Resolve).
  - **Turnaround Model Sheet:** Front, 3/4, Profile, and Back angles for 3D animators and costume designers.
  - **Era / Wardrobe Variants:** Battle attire, casual, period-specific clothing.
- **Consistency Locking:** Generates character seed IDs and visual prompt fingerprints passed directly to `StoryboardEngine`.

### 3. API Endpoints
- `POST /characters/{character_id}/generate-concept-art` — Generates concept portrait.
- `POST /characters/{character_id}/generate-expression-sheet` — Generates 6-expression matrix.
- `POST /characters/{character_id}/generate-turnaround` — Generates turnaround model sheet.
- `GET /projects/{project_id}/export/character-lookbook.pdf` — Multi-page executive casting look-book.

### 4. Frontend UX Deliverables
- **Interactive Character Studio Tab:** Inside `CharacterLibraryView.tsx` with instant portrait generation and turnaround gallery.
- **Expression Switcher:** Preview character expressions with one click.

---

## 📖 Phase 9: The Graphic Novel Creation Studio

### 1. Objective & Capabilities
A complete comic and graphic novel publishing platform. Transforms screenplays and prose into fully formatted, lettered, multi-panel comic book pages ready for digital publishing or physical print.

### 2. Comic Layout & Lettering Architecture
- **New Engine Module:** `backend/graphic_novel_engine.py` & `backend/lettering_service.py`
- **Core Components:**
  1. **Dynamic Multi-Panel Grid Engine:**
     - Computes optimum panel distribution per page (1 to 9 panels) based on narrative pacing, emotional beats, and action climaxes.
     - Layout templates: Standard 6-panel grid, Wide 3-tier cinematic, Manga vertical stagger, Full-page splash, Inset panels.
  2. **Smart Dialogue Balloon & Caption Placement:**
     - AI bounding-box analysis (detects empty negative space and character eyelines).
     - Automatically places speech bubbles with tail vectors pointing toward speaking characters.
     - Narrative caption boxes for scene headings and voice-over prose.
  3. **Letterer Typography & Sound Effects (SFX):**
     - Professional comic typography (*Bangers*, *Comic Neue*, *Action Man*, *Blambot* fonts).
     - Dynamic vector Sound Effect graphics (*WHAM!*, *SKRRRRT!*, *KABOOM!*, *CLICK!*) tailored to scene action tags.
  4. **Art Style Continuity Lock:**
     - Integrates with Style Vault (e.g. `comic_book`, `european_graphic_novel`, `manga_kinetic`, `film_noir`, `painted_realism`).
     - Maintains consistent ink weight, halftone shading, and color grading across all pages.

### 3. Database Schema Extensions
```python
class ComicPage(Base):
    __tablename__ = "comic_pages"
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"))
    page_number = Column(Integer)
    layout_type = Column(String)  # 6_panel_grid, splash, 3_tier_cinematic, manga_stagger
    rendered_page_path = Column(String, nullable=True)

class ComicPanel(Base):
    __tablename__ = "comic_panels"
    id = Column(String, primary_key=True)
    page_id = Column(String, ForeignKey("comic_pages.id"))
    panel_index = Column(Integer)
    scene_id = Column(String, nullable=True)
    image_path = Column(String)
    crop_x = Column(Float)
    crop_y = Column(Float)
    crop_w = Column(Float)
    crop_h = Column(Float)
    speech_balloons_json = Column(Text)  # [{"speaker": "KIRK", "text": "...", "x": 0.2, "y": 0.1}]
```

### 4. Master Comic Exporters
- `GET /projects/{project_id}/export/graphic-novel.pdf` — High-res 300 DPI CMYK print PDF with crop marks and gutter bleeds.
- `GET /projects/{project_id}/export/graphic-novel.cbz` — Standard `.cbz` archive with `ComicInfo.xml`.
- `GET /projects/{project_id}/export/webtoon.zip` — Vertical scroll PNG strips formatted for Webtoon / Tapas mobile reading.

### 5. Frontend UX Deliverables
- **New Studio View:** `frontend/src/components/GraphicNovelStudio.tsx`
- **Interactive Page Canvas:** Drag-and-drop panel resizer, speech balloon editor, and live page spread previewer.
- **Webtoon Mode Toggle:** Switch seamlessly between traditional two-page book spreads and vertical mobile scrolls.

---

## 🗓️ Implementation Sequence & Milestones

| Phase | Milestone | Primary Deliverable | Est. Scope |
|:---|:---|:---|:---:|
| **Phase 4** | **Multimodal Animatics** | Video generation adapters, frame motion player, `.mp4` reel exporter | 3 Days |
| **Phase 5** | **AI Story Doctor** | 15-beat analyzer, narrative arc visualizer, coverage report | 2 Days |
| **Phase 6** | **Universal Comic/ePub** | `.cbz`, `.cbr`, `.epub` parsers & round-trip archive exporter | 2 Days |
| **Phase 7** | **Virtual Table Read** | Synchronized multi-voice teleprompter studio & stem generator | 3 Days |
| **Phase 8** | **Character Studio** | Multi-angle model sheets, expression matrices, look-book PDF | 2 Days |
| **Phase 9** | **Graphic Novel Studio** | Dynamic panel layouts, smart speech balloon placement, Webtoon / Print PDF export | 4 Days |

---

## 🛡️ Governance & Copyright Commitment
All generative pipelines strictly adhere to **Kirk LaSalle's Permanent Active Directives (The 10 Laws)** and the **PRISM Sacred Covenant**:
- **Copyright Sovereignty:** 100% of generated scripts, prompts, character designs, storyboards, animatics, and graphic novels remain the exclusive intellectual property of Kirk LaSalle.
- **Human Memory Model:** Intermediate training weights and raw document caches are purged; only distilled craft wisdom is retained in the Second Brain.
- **Codebase Integrity:** Zero regressions on existing 75 unit tests and format parsing speeds (< 0.5ms).
