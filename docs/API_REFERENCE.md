# REST API Reference — CineMatrix Studio

**Base URL:** `http://127.0.0.1:8000`
**API version:** 3.3.0 (single-sourced from `APP_VERSION` in `backend/main.py`)
**Standard:** OpenAPI 3.0 / FastAPI
**Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`
**Last verified against source:** 2026-10-14 — **60 routes**

> ⚠️ **Security note.** The API has no authentication and is intended for loopback use only. CORS is restricted to `localhost` / `127.0.0.1` origins. `POST /system/shutdown` terminates the process for any caller that can reach it. Never bind CineMatrix to a non-loopback interface. See [STATUS.md](./STATUS.md) §5.

---

## 1. System & Service

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/health` | Service health, name, version, and UTC timestamp. |
| `GET` | `/` | Service status, tagline, version, and docs URL. |
| `POST` | `/system/shutdown` | Gracefully terminate the studio process with PRISM audit logging. |
| `GET` | `/agreement` | Return the full User Content Agreement. |
| `GET` | `/governance` | Return the governance framework and the 10 Laws. |

---

## 2. Projects & Script Ingestion

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/projects` | List all projects with scene, frame, and character telemetry. |
| `POST` | `/projects` | Create a new project. |
| `GET` | `/projects/{project_id}` | Project detail with persisted scenes and frames. |
| `DELETE` | `/projects/{project_id}` | Delete a project and all child records. |
| `POST` | `/projects/{project_id}/scripts` | Upload a screenplay (`.fdx`, `.fountain`, `.docx`, `.pdf`, `.txt`, `.cbz`, `.cbr`, `.epub`). Format is auto-detected; 20 MB cap. |
| `GET` | `/projects/{project_id}/scenes` | List persisted scenes for a project. |

> **Correction:** earlier revisions of this document listed `POST /projects/upload`. That endpoint has never existed — use `POST /projects/{project_id}/scripts`.

---

## 3. Example Script Library

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/examples` | Catalog of the 27 sample scripts. Optional `?category=` filter (`formats`, `engines`, `genres`, `durations`). |
| `GET` | `/examples/{category}/{filename}` | Content or preview of one sample script. |
| `POST` | `/projects/{project_id}/load-example` | Load a sample script into an existing project. Body: `{"category": "...", "filename": "..."}`. |
| `POST` | `/projects/create-with-example` | One-click create-and-populate a project from a sample script. |

Path components are validated for containment within the examples directory; traversal attempts return `400 Bad Request`.

---

## 4. Storyboard Generation

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/styles` | List the 16 visual aesthetic style presets. |
| `POST` | `/projects/{project_id}/generate` | Generate storyboard scenes and frames for a project. |
| `POST` | `/projects/{project_id}/generate-stream` | Server-Sent Events stream of generation progress and frames. |
| `POST` | `/frames/{frame_id}/generate-image` | Generate or regenerate the image for one frame. |
| `POST` | `/projects/{project_id}/generate-all-images` | Batch render images for every frame in a project. |

---

## 5. Animatics & Video

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/video/presets` | List the 6 camera motion presets. |
| `POST` | `/frames/{frame_id}/generate-animatic` | Synthesize a sub-pixel Ken Burns motion clip (`.mp4`) for one frame. |
| `POST` | `/projects/{project_id}/generate-all-animatics` | Batch generate animatics for every frame. |
| `GET` | `/projects/{project_id}/export/animatic-reel.mp4` | Download the stitched master animatic reel with title cards. |

---

## 6. AI Story Doctor & Narrative Structure

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/projects/{project_id}/analysis/beat-sheet` | Blake Snyder 15-beat structural breakdown and scene mappings. |
| `GET` | `/projects/{project_id}/analysis/narrative-arc` | Time-series dramatic tension and pacing arc. |
| `GET` | `/projects/{project_id}/analysis/coverage` | Executive studio coverage analysis. |
| `POST` | `/projects/{project_id}/analysis/story-doctor/chat` | Ask the interactive Story Doctor assistant, with project context. |

---

## 7. Characters, Casting & Table Read

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/characters/library` | Global character archetype library. Supports `?limit=`. |
| `GET` | `/characters/library/stats` | Character library statistics. |
| `GET` | `/characters/library/taxonomy` | Full character taxonomy (roles x archetypes x tiers x genres). |
| `GET` | `/projects/{project_id}/characters` | Characters profiled for a project. |
| `PATCH` | `/projects/{project_id}/characters/{character_id}` | Update voice assignment or visual-consistency prompt. |
| `POST` | `/characters/audition` | Generate a live voice audition sample / character profile. |
| `GET` | `/projects/{project_id}/readthrough/cast` | Cast list with assigned TTS voices. |
| `GET` | `/projects/{project_id}/readthrough/scene/{scene_number}` | Synchronized dialogue cues and speech cadence timeline. |
| `POST` | `/projects/{project_id}/readthrough/generate` | Generate a virtual table-read audio performance. |

---

## 8. Graphic Novel & Print Studio

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/graphic-novel/layouts` | List the multi-panel layout presets (1-Splash through 9-Panel and Webtoon). |
| `GET` | `/projects/{project_id}/graphic-novel/pages` | Paginate scenes into comic pages with balloon placement. Supports `?layout=`. |
| `GET` | `/projects/{project_id}/export/graphic-novel-print.pdf` | Download the 300 DPI CMYK-ready print PDF edition. |

---

## 9. Procedural Audio & Foley

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/audio/score-presets` | List the procedural soundtrack mood presets. |
| `GET` | `/audio/sfx-presets` | List the procedural foley effect presets. |
| `POST` | `/audio/score/generate` | Synthesize a 16-bit 44.1 kHz stereo WAV soundtrack. |
| `POST` | `/audio/sfx/generate` | Synthesize a foley sound effect. |

---

## 10. Master Exporters

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/projects/{project_id}/export/storyboard.pdf` | 16:9 landscape executive PDF presentation deck. |
| `GET` | `/projects/{project_id}/export/images.zip` | ZIP archive of all rendered frames with a CSV metadata index. |
| `GET` | `/projects/{project_id}/export/storyboard.cbz` | Comic Book Archive with `ComicInfo.xml`. |
| `GET` | `/projects/{project_id}/export/character-lookbook.pdf` | Casting & Character Look-Book PDF deck. |
| `GET` | `/projects/{project_id}/export/shot-list.csv` | Production camera shot list CSV. |
| `GET` | `/projects/{project_id}/export/script.fountain` | Re-exported Fountain screenplay. |

See also section 5 for `animatic-reel.mp4` and section 8 for `graphic-novel-print.pdf` — eight export endpoints in total.

---

## 11. AI Provider Configuration

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/providers/config` | Current provider configuration. API keys are masked in the response. |
| `POST` | `/providers/save` | Persist provider configuration. Keys are encrypted at rest. |
| `POST` | `/providers/test` | Test connectivity for a provider configuration. |
| `POST` | `/providers/models` | List available models for a provider. |
| `POST` | `/providers/balance` | Query account balance where the provider supports it. |
| `GET` | `/providers/image-status` | Report configured image-generation provider status. |
| `GET` | `/providers/local/models` | Query locally hosted model names (Ollama / Stable Diffusion). |

Supported providers: **OpenAI**, **Anthropic**, **Google GenAI**, **Groq**, **OpenRouter**, and **Local**.

---

## 12. Cinematic Knowledge Base

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/knowledge` | List cinematic knowledge-base entries. |
| `GET` | `/knowledge/stats` | Knowledge-base statistics. |
| `POST` | `/knowledge/learn` | Add a knowledge entry. |

---

## 13. Static Assets

| Path | Description |
|:---|:---|
| `/static/...` | Generated media (rendered frames, animatic clips, audio stems) served from `backend/static/`. |

---

## Error Semantics

| Status | Meaning |
|:---|:---|
| `400` | Invalid request body, unsupported/empty content, or a rejected example path. |
| `404` | Project, frame, character, or example file not found. |
| `500` | Unhandled server error. |

> **Known limitation.** The global exception handler currently returns raw exception text in `detail`, which can disclose internal paths and provider errors. A sanitised error envelope with correlation IDs is scheduled for Phase 11 — see [ROADMAP.md](./ROADMAP.md).
