# User Guide — CineMatrix Studio

**Author:** Kirk LaSalle  
**Governance:** PRISM Sacred Covenant & Permanent Active Directives (The 10 Laws)  
**Standard:** Level 3 — Oscar / World-Class Prestige  
**Applies to:** v3.3.0

---

## 1. Getting Started

### 1.1 One-Click Launch
Double-click `start_storyboard.bat` (or execute `./start_storyboard.ps1` in PowerShell).  
This automatically starts:
- **FastAPI Backend Server:** `http://127.0.0.1:8000`
- **React Frontend Studio:** `http://localhost:5173`
- Your default web browser will open to the **Projects Hub**.

### 1.2 Connect a Provider
Open **Provider Configuration** (shortcut `9`) and add a key for OpenAI, Anthropic, Google, Groq, OpenRouter, or a local endpoint. Use **Test Connection** to confirm it works before generating. Keys are stored encrypted on your machine and are never transmitted anywhere except to the provider you selected.

> CineMatrix is a local-only studio with no login. Do not expose it beyond `localhost` — see [../SECURITY.md](../SECURITY.md).

---

## 2. The 9 Workspaces

The heading numbers below are the `1`–`9` keyboard shortcuts: `1` Projects Hub, `2` Script Uploader, `3` Storyboard Gallery, `4` Characters, `5` Table Read, `6` Story Doctor, `7` Graphic Novel, `8` Examples, `9` Configuration.

### 1. Projects Hub
- View all saved screenplay projects, scene counts, frame counts, and cast metrics.
- Upload scripts in `.fdx`, `.fountain`, `.docx`, `.pdf`, `.txt`, `.cbz`, `.cbr`, or `.epub` format.
- Download quick PDF decks directly from project cards.

### 2. Script Uploader
- Drag and drop a screenplay, or paste raw text, to create a new project.
- Format is detected by both file extension and magic bytes, so mislabelled files still parse.

### 3. Storyboard Gallery
- Switch between **16 Visual Styles** (Oscar Prestige, Cyberpunk, Nordic Noir, Vintage Noir, Anime, etc.).
- Inspect individual scenes, camera shot types, and dramatic intensity scores.
- Trigger single-frame image generations or bulk generation.
- Click **"Animate Frame"** on any card to render a 24 FPS animatic using one of 6 camera motion presets: `Dolly In`, `Dolly Out`, `Pan Left`, `Pan Right`, `Handheld`, `Slow-Mo Drift`.
- Access the **Master Export Suite** dropdown for PDF decks, shot-list CSV, ZIP archives, the master MP4 reel, Fountain script, CBZ packages, and procedural audio stems.

### 4. Characters & Casting Studio
- Browse cast members mapped to a Jungian archetype taxonomy.
- Audition character voices live using 6 TTS vocal models (`alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`).
- Re-assign voice profiles and customize visual consistency prompt look-books.
- Generate 4-angle turnaround model sheets (Front, 3/4, Profile, Back) and 6-expression matrices (Neutral, Anger, Joy, Calculation, Sorrow, Resolve), then export an executive **Casting Look-Book PDF Deck**.

### 5. Virtual Table Read Studio
- Select any screenplay scene to open the **Synchronized Teleprompter**.
- Hit **"Start Table Read"** to watch the prompter autoscroll in real-time with speaking character highlights.
- Click the speaker icon next to any line to audition that dialogue cue instantly.

### 6. AI Story Doctor & Beat Sheet Analyzer
- View screenplay scenes automatically classified against Blake Snyder's **15 Screenplay Milestones** (*Opening Image*, *Catalyst*, *Midpoint*, *All Hope is Lost*, *Finale*, etc.).
- Analyze the **Narrative Tension Arc Graph** across Acts I, IIA, IIB, and III.
- Consult the interactive **Story Doctor chat** for dialogue punch-ups, subtext sharpening, and third-act twists.

### 7. Graphic Novel Creation Studio
- Choose from 7 dynamic panel layout templates:
  - `1-Panel Splash Page`
  - `2-Panel Widescreen Split`
  - `3-Panel Classic Strip`
  - `4-Panel Action Quadrant`
  - `6-Panel Manga / European Grid`
  - `9-Panel Watchmen Grid`
  - `Vertical Webtoon Continuous Scroll`
- Preview smart speech balloons and caption boxes positioned over panels.
- Export a **300 DPI CMYK Print PDF** or standard **.CBZ Comic Archive**.

### 8. Example Scripts Hub
- Browse the 27-script sample library across Universal Formats, Engine Showcases, Genres & Styles, and Duration Tiers.
- Preview any script in place, or create a fully populated project from it in one click.

### 9. Provider Configuration
- Add, test, and switch AI providers and models for text and image generation.
- Review which capabilities are available for the currently selected provider.

> **Universal ingestion** (`.cbz`, `.cbr` with `ComicInfo.xml` extraction, and `.epub` with automatic chapter partitioning) is a platform-wide capability available from the Projects Hub and Script Uploader — it is not a separate workspace.

---

## 3. Director Pitch & Presentation Mode (Keynote Fullscreen)

Click **"Pitch Mode"** in the Storyboard Gallery header to enter fullscreen presentation mode:
- **Space** or **→**: Advance to next scene
- **←**: Previous scene
- **F**: Toggle Fullscreen
- **N**: Toggle Director Notes / Dialogue Teleprompter
- **Esc**: Exit Presentation Mode
