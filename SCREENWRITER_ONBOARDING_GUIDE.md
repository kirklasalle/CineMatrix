# CineMatrix Studio v3.3 — Screenwriter & Creator Onboarding Guide
> **"From Final Draft to Animatics, Table Read & 300 DPI Graphic Novel in 60 Seconds."**  
> **Founder & Sovereign Architect:** Kirk LaSalle  
> **Platform Version:** 3.3.0 (Oscar Prestige Edition)
> **Repository:** [github.com/kirklasalle/CineMatrix](https://github.com/kirklasalle/CineMatrix)

---

## Welcome to the Future of Visual Storytelling

Traditional film pre-production is slow and exorbitantly expensive: hiring human storyboard artists costs indie filmmakers between **$15,000 and $50,000 per feature film**, requiring weeks of back-and-forth sketches.

**CineMatrix Studio** replaces this bottleneck with an Oscar-tier, local-first pre-visualization ecosystem in a box. In under 60 seconds, CineMatrix digests your raw screenplay, breaks down every scene into dramatic beats, generates camera shot compositions, auditions multiple voice actors for table reads, audits narrative pacing via Blake Snyder’s 15-beat dramaturgy, and compiles full-motion animatics and print-ready graphic novels.

---

## 1. Quickstart: Launching CineMatrix Studio

CineMatrix runs completely private on your local machine with zero cloud lock-in.

### 1-Click Desktop Startup (Release Bundle)
The only prerequisite is **Python 3.12, 3.13, or 3.14** — 3.14 recommended ([python.org](https://www.python.org/downloads/)). If several versions are installed, the launcher picks a supported one automatically; Python 3.15 is not supported yet. Node.js is **not** required.

1. Unzip the release download (for example `CineMatrix-Studio-v3.3.0-creator-beta.zip`) to a folder of your choice.
2. Double-click **`start_cinematrix.bat`** in that folder.
3. CineMatrix will automatically:
   - Locate a supported Python (3.12–3.14).
   - On first run only, create a private `.venv` environment and install dependencies (a few minutes; needs internet).
   - Boot the secure FastAPI backend on `http://127.0.0.1:8000`.
   - Serve the CineMatrix interface on `http://127.0.0.1:5173`.
   - Open a dedicated, distraction-free desktop application window.

> [!NOTE]
> **Running from a source checkout instead?** Developers working from the Git repository also need Node.js 18+; `python desktop_launcher.py` starts the Vite dev server on `http://localhost:5173`. See the [Developer Guide](https://github.com/kirklasalle/CineMatrix/blob/main/docs/DEVELOPER_GUIDE.md).

> [!TIP]
> **Graceful Shutdown**: When finished, click the **Shutdown** button in the top-right header or press `Ctrl+C` in the terminal. CineMatrix cleanly commits all SQLite databases and flushes temp caches.

---

## 2. The Universal Screenplay Ingestion Matrix

CineMatrix accepts your stories in whatever format you write:

| Format | Extension | Capabilities in CineMatrix |
| :--- | :--- | :--- |
| **Final Draft** | `.fdx` | Full scene headings, character names, parentheticals, and dialogue tokens. |
| **Fountain** | `.fountain` | Industry standard plaintext screenplay markup. |
| **Microsoft Word** | `.docx` | Formatted treatment or script documents. |
| **Adobe PDF** | `.pdf` | Industry standard shooting scripts and reader drafts. |
| **Comic Archives** | `.cbz`, `.cbr` | Graphic novels and comics for visual shot style ingestion. |
| **ePub Books** | `.epub` | Novels and narrative manuscripts for chapter-by-scene adaptation. |

### How to Ingest a Script:
1. Press key **`2`** or navigate to **Script Ingestion**.
2. Drag and drop your `.fdx`, `.fountain`, or `.pdf` file into the upload zone.
3. CineMatrix automatically extracts:
   - Scene numbers and headings (`INT. CYBERPUNK LAB - NIGHT`)
   - Character identities and dialogue lines
   - Emotional intensity scores and dramatic action beats

---

## 3. The 9 Dedicated Creative Studios

CineMatrix organizes your creative pre-production into 9 specialized workspaces:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 THE 9 CREATIVE STUDIOS                                 │
├─────────┬────────────────────────────┬─────────────────────────────────────────────────┤
│ Hotkey  │ Studio Name                │ Core Creative Capability                        │
├─────────┼────────────────────────────┼─────────────────────────────────────────────────┤
│ [ 1 ]   │ Projects Hub               │ Master portfolio, script history, and telemetry │
│ [ 2 ]   │ Script Ingestion & Parser  │ Multi-format import (.fdx, .fountain, .pdf)     │
│ [ 3 ]   │ Storyboard Gallery         │ Shot direction, camera types, and animatics     │
│ [ 4 ]   │ Cast & Character Vault     │ Consistent visual archetypes & reference sheets │
│ [ 5 ]   │ Virtual Table Read         │ Multi-voice AI dialogue auditioning & playback  │
│ [ 6 ]   │ AI Story Doctor            │ Blake Snyder 15-beat narrative flow diagnostics │
│ [ 7 ]   │ Graphic Novel Studio       │ 300 DPI CMYK print export (comic book layout)   │
│ [ 8 ]   │ Script Examples Library    │ 27 pre-analyzed Hollywood master screenplays    │
│ [ 9 ]   │ Provider Configuration     │ Local SLM (Ollama) vs. Cloud (Claude/OpenAI)    │
└─────────┴────────────────────────────┴─────────────────────────────────────────────────┘
```

### Studio Deep-Dives:

#### Studio 3: Storyboard Gallery & Camera Direction
- **Camera Types**: Select from Extreme Wide Shot, Master Wide, Medium Close-Up, Extreme Close-Up, Low-Angle Hero, High-Angle Bird's Eye, and Dutch Tilt.
- **Dynamic Camera Motion**: Apply cinematic Ken Burns motion presets: *Pan Left/Right*, *Slow Push-In*, *Dramatic Pull-Back*, *Subtle Handheld Drift*.
- **Animatic Generation**: Render stitched `.mp4` video animatics with synchronized scene audio moods and pacing.

#### Studio 4: Cast & Character Consistency Vault
- Avoid "face-drifting" in AI images. CineMatrix locks character visual traits (hair, eyes, age, costume, facial structure) across all subsequent storyboard panels.

#### Studio 5: Virtual Table Read Studio
- Assign distinct voice actors to every character in your script. Audition dialogue beats before stepping onto set or pitching to financiers.

#### Studio 6: AI Story Doctor (15-Beat Dramaturgy)
- Audits your script against Blake Snyder’s *Save the Cat!* structural milestones:
  - *Opening Image (p. 1)* &rarr; *Theme Stated (p. 5)* &rarr; *Set-Up (pp. 1-10)*
  - *Catalyst (p. 12)* &rarr; *Debate (pp. 12-25)* &rarr; *Break into Two (p. 25)*
  - *B Story (p. 30)* &rarr; *Fun and Games (pp. 30-55)* &rarr; *Midpoint (p. 55)*
  - *Bad Guys Close In (pp. 55-75)* &rarr; *All Hope is Lost (p. 75)*
  - *Dark Night of the Soul (pp. 75-85)* &rarr; *Break into Three (p. 85)*
  - *Finale (pp. 85-110)* &rarr; *Final Image (p. 110)*
- Highlights pacing drags, missing catalysts, and climax tension deficits.

#### Studio 7: Graphic Novel Studio (300 DPI CMYK)
- Transform your screenplay into a published comic book or graphic novel.
- Supports 4-panel, 6-panel, and 9-panel grid systems with automated speech balloon positioning and print-ready PDF export.

---

## 4. Professional NLE Keyboard Shortcuts (Avid / Premiere / Resolve)

CineMatrix is built with the muscle memory of seasoned Hollywood editors and animators:

### Studio Quick-Switch (Keys 1 – 9)
Tap any number key (`1` through `9`) to instantly switch between studios without touching your mouse:
- `1`: Projects Hub
- `2`: Script Ingestion
- `3`: Storyboard Gallery
- `4`: Character Cast
- `5`: Table Read
- `6`: Story Doctor
- `7`: Graphic Novel
- `8`: Examples Library
- `9`: Configuration

### J-K-L Playback & Audition Controls
- **`Spacebar`**: Audition / Play-Pause slideshow and animatics reel.
- **`L`** or **`→`**: Step Forward / advance to the next beat.
- **`K`**: Pause Playback.
- **`J`** or **`←`**: Step Backward / rewind to previous beat.
- **`Home` / `End`**: Jump directly to First or Last frame.

### Presentation & Help Controls
- **`F`**: Toggle Fullscreen Presentation Mode (ideal for projecting in pitch meetings).
- **`N`**: Toggle Director Notes and dramatic intensity scores.
- **`?`** or **`/`**: Open the on-screen NLE Shortcuts Reference Cheat Sheet.
- **`Esc`**: Exit Fullscreen or dismiss open modals.

> [!NOTE]
> Keyboard hotkeys are intelligently suspended whenever your cursor is inside a text input, search box, or prompt editor.

---

## 5. Exporting Your Deliverables

When your visual pre-production is complete, export high-prestige assets directly:
1. **Director Pitch Deck (PDF)**: High-resolution cover, scene breakdown, character profiles, and full-color shot sheets.
2. **Master Video Animatic (.mp4)**: Ken Burns pan/zoom stitched video reel with scene narration and mood scoring.
3. **Graphic Novel Print Book (300 DPI PDF)**: Ready for print-on-demand publication or visual pitch meetings with studio executives.
4. **Scene CSV Data**: Raw scene breakdowns for production coordinators and 1st Assistant Directors.

---

## 6. Privacy, Security & Sovereign Data Guarantee

Under Kirk LaSalle’s Permanent Active Directives:
- **Zero Cloud Leakage**: Your unproduced screenplays, concepts, and dialogue remain strictly on your local computer (`backend/database/storyboard.db`).
- **Offline Capable**: Connect to local Ollama models (Llama 3, Mistral) for 100% offline generation without sending a single byte over the Internet.
- **100% Creator IP Ownership**: You retain full, unencumbered intellectual property rights over all generated storyboards, animatics, and graphic novels.

---

*CineMatrix Studio · Engineered for Creators by Kirk LaSalle & Antigravity AI.*
