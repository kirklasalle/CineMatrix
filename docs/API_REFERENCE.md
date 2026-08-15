# REST API Reference — Storyboard AI

**Base URL:** `http://127.0.0.1:8000`  
**Standard:** OpenAPI 3.0 / FastAPI  
**Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`  

---

## 1. Projects & Scripts

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/projects` | List all saved projects with scene, frame, and cast telemetry. |
| `GET` | `/projects/{id}` | Get detailed project information and scene breakdown. |
| `POST` | `/projects/upload` | Upload a screenplay file (`.fdx`, `.fountain`, `.docx`, `.pdf`, `.cbz`, `.epub`). |
| `DELETE` | `/projects/{id}` | Delete a project and all associated frames and characters. |

---

## 2. Storyboards & Visual Styles

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/styles` | List all 16 visual aesthetic style presets with descriptions. |
| `GET` | `/projects/{id}/frames` | Retrieve all analyzed storyboard frames for a project. |
| `POST` | `/frames/{id}/generate-image` | Generate or re-generate an image for a specific storyboard frame. |
| `POST` | `/projects/{id}/generate-all-images` | Trigger bulk generation for all storyboard frames in a project. |

---

## 3. Multimodal Animatics & Video

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/video/presets` | List all 6 camera motion animatic presets. |
| `POST` | `/frames/{id}/generate-animatic` | Synthesize a sub-pixel camera motion video clip (`.mp4`) for a frame. |
| `GET` | `/projects/{id}/export/animatic-reel.mp4` | Download the master stitched animatic video reel with title cards. |

---

## 4. AI Story Doctor & Narrative Structure

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/projects/{id}/analysis/beat-sheet` | Return Blake Snyder 15-beat structural breakdown and scene mappings. |
| `GET` | `/projects/{id}/analysis/narrative-arc` | Return time-series dramatic tension and pacing arc. |
| `GET` | `/projects/{id}/analysis/coverage` | Return executive studio coverage analysis. |
| `POST` | `/projects/{id}/analysis/story-doctor/chat` | Send question to the interactive AI Story Doctor assistant. |

---

## 5. Casting & Table Read Studio

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/projects/{id}/readthrough/cast` | List all characters with assigned TTS voices. |
| `GET` | `/projects/{id}/readthrough/scene/{scene_number}` | Get synchronized dialogue cues and speech cadence timeline. |
| `POST` | `/characters/audition` | Generate live audio sample for character voice audition. |
| `PATCH` | `/projects/{id}/characters/{char_id}` | Update character voice assignment or visual consistency prompt. |

---

## 6. Graphic Novel & Print Studio

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/graphic-novel/layouts` | List all 7 multi-panel graphic novel layout presets. |
| `GET` | `/projects/{id}/graphic-novel/pages` | Paginate scenes into formatted comic pages with speech balloons. |
| `GET` | `/projects/{id}/export/graphic-novel-print.pdf` | Download 300 DPI CMYK Print PDF edition. |

---

## 7. Master Exporters

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/projects/{id}/export/storyboard.pdf` | Download 16:9 Landscape Executive PDF deck. |
| `GET` | `/projects/{id}/export/images.zip` | Download full ZIP archive of all rendered frames. |
| `GET` | `/projects/{id}/export/storyboard.cbz` | Download standard Comic Book Archive with `ComicInfo.xml`. |
| `GET` | `/projects/{id}/export/character-lookbook.pdf` | Download Casting & Character Look-Book PDF deck. |
| `GET` | `/projects/{id}/export/shot-list.csv` | Download production CSV camera shot list. |
| `GET` | `/projects/{id}/export/script.fountain` | Download re-exported Fountain screenplay. |

---

## 8. Procedural Audio & Foley

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/audio/score-presets` | List procedural soundtrack mood presets. |
| `GET` | `/audio/sfx-presets` | List procedural foley sound effects presets. |
| `POST` | `/audio/score/generate` | Synthesize a 16-bit stereo WAV soundtrack track. |
| `POST` | `/audio/sfx/generate` | Synthesize a foley sound effect. |
