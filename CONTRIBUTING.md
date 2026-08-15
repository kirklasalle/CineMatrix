# Contributing to CineMatrix

First off, thank you for considering contributing to **CineMatrix**! CineMatrix is built by and for filmmakers, screenwriters, animators, and software engineers who believe in open, local-first storytelling tools.

---

## 🛠️ Development Setup

### 1. Prerequisites
- **Python 3.10+** (Python 3.11/3.12 recommended)
- **Node.js 18+** & **npm**
- **Git**

### 2. Fork and Clone
```bash
git clone https://github.com/kirklasalle/CineMatrix.git
cd CineMatrix
```

### 3. Backend Setup
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
pip install pytest httpx
```

### 4. Frontend Setup
```bash
cd ../frontend
npm install
```

### 5. Running the Local Dev Environment
- **Backend**: `python backend/main.py` (Runs on `http://127.0.0.1:8000`)
- **Frontend**: `cd frontend && npm run dev` (Runs on `http://localhost:5173`)

---

## 🧪 Testing Guidelines

Before opening a pull request, ensure all tests pass and the frontend compiles:

```bash
# Run backend test suite
python -m pytest backend/tests/ -v

# Run frontend build
cd frontend && npm run build
```

---

## 📐 Project Structure

```
CineMatrix/
├── backend/
│   ├── database/             # SQLite models and migrations
│   ├── parsers/              # Final Draft, Fountain, PDF, DOCX, EPUB, CBZ parsers
│   ├── providers/            # Multi-provider LLM & image generation clients
│   ├── tests/                # Automated pytest suite (104 tests)
│   ├── audio_scoring_engine.py   # 44.1kHz procedural music & foley synthesizer
│   ├── concept_art_engine.py     # 4-angle turnarounds & 6-expression model sheets
│   ├── graphic_novel_engine.py   # Dynamic panel layouts & 300 DPI PDF publisher
│   ├── story_doctor.py           # Blake Snyder 15-beat sheet & tension arc
│   ├── table_read_orchestrator.py # Multi-voice speech cadence & teleprompter
│   ├── video_engine.py           # 24 FPS OpenCV camera motion animatics
│   └── main.py                   # FastAPI application & REST endpoints
├── frontend/
│   ├── src/
│   │   ├── components/       # React UI studio views & modals
│   │   ├── App.tsx           # Main application state & navigation
│   │   └── index.css         # Glassmorphism design tokens & styles
├── docs/
│   ├── examples/             # 27 curated sample screenplays
│   ├── images/               # Documentation illustrations & architecture flow
│   ├── API_REFERENCE.md      # REST API documentation
│   ├── DEVELOPER_GUIDE.md    # Architecture deep-dive
│   └── USER_GUIDE.md         # Director & screenwriter user manual
```

---

## 📜 Code Style & Philosophy

- **Local-First & Resilient**: Tools should work offline with deterministic fallbacks when external API keys are not supplied.
- **Cinematic Authenticity**: Features must respect real-world optics (focal lengths, shutter angles, lighting ratios).
- **Creator Ownership**: User scripts and generated media remain 100% private and under the creator's control.
