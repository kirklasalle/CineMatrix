# CineMatrix Studio — Project Status

**Document owner:** Kirk LaSalle
**Last updated:** 2026-10-14
**Current version:** 3.3.0
**Release channel:** Early Adopter Creator Desktop Release
**Overall state:** 🟢 **Buildable, tested, and runnable** — cleared for creator beta; two hardening phases outstanding before a public commercial release.

> This is the single source of truth for "where is CineMatrix right now?".
> Update it with every release. Detailed findings live in [AUDIT_2026-10-14.md](./AUDIT_2026-10-14.md); forward plans live in [ROADMAP.md](./ROADMAP.md).

---

## 1. At a Glance

| | |
|---|---|
| **Version** | 3.3.0 — Integrity & Reliability Release |
| **Previous version** | 3.2.0 (2026-08-14) |
| **Repository** | [`kirklasalle/CineMatrix`](https://github.com/kirklasalle/CineMatrix) |
| **Backend** | FastAPI 0.139 · Python 3.14 (CI: 3.12) · 60 REST endpoints |
| **Frontend** | React 18 · TypeScript 5.2 (strict) · Vite 5 · Tailwind 3 |
| **Tests** | **117 passing** (backend, ~15s) · 0 failing · 0 skipped |
| **Build** | ✅ `tsc` clean · ✅ Vite production build clean |
| **Lint** | ✅ Exit 0 (84 warnings tracked for Phase 13) |
| **CI** | ✅ Green — backend pytest + frontend lint & build |
| **Open critical defects** | **0** |
| **Open high-severity defects** | **1** (H-2, fail-open encryption — scheduled Phase 11) |

---

## 2. Health Dashboard

| Area | Status | Notes |
|---|---|---|
| Install from clean checkout | 🟢 Healthy | Fixed in 3.3.0 — was broken in 3.2.0 and earlier |
| Backend boot | 🟢 Healthy | 65 routes register; governance integrity check passes |
| Test suite | 🟢 Healthy | 117/117 passing |
| Frontend build & typecheck | 🟢 Healthy | Strict TypeScript, no errors |
| CI pipeline | 🟢 Healthy | Repaired in 3.3.0 — previously could not install dependencies |
| Lint enforcement | 🟡 Partial | Config restored; 84 warnings to clear (Phase 13) |
| Security | 🟡 Hardening | Traversal fixed; encryption, uploads, error envelope pending (Phase 11) |
| Performance under load | 🟡 Known debt | Blocking work in async handlers; no job queue (Phase 12) |
| Frontend test coverage | 🔴 None | No test runner yet (Phase 13) |
| Cross-platform support | 🟡 Windows-first | Launcher hardcodes Windows browser paths (Phase 14) |

---

## 3. What Works Today

All of the following are implemented, wired, and verified:

### Creative studios (6)
1. **Storyboard Gallery** — auto image generation, camera/lighting spec bar, batch render, lightbox, SSE streaming.
2. **24 FPS Animatics Studio** — local OpenCV sub-pixel Ken Burns motion, 6 camera presets, master MP4 reel compiler.
3. **AI Story Doctor** — Blake Snyder 15-beat classifier, narrative tension curve, executive coverage, interactive chat.
4. **Virtual Table Read Studio** — synchronized teleprompter, ~150 WPM cadence model, 6-voice line auditioning.
5. **Character & Casting Library** — archetype taxonomy, voice assignment, visual-consistency prompt injection, model sheets.
6. **Graphic Novel Studio** — multi-panel layout engine, balloon placement, 300 DPI print PDF, CBZ export.

### Supporting views (3)
7. **Projects Hub** · 8. **Example Scripts Hub** (27 scripts) · 9. **Provider Configuration**

### Platform capabilities
- **Ingestion:** `.fdx`, `.fountain`, `.docx`, `.pdf`, `.txt`, `.cbz`, `.cbr`, `.epub` with magic-byte format detection.
- **Export:** 16:9 PDF deck, shot-list CSV, ZIP frame archive, CBZ, character look-book PDF, 300 DPI graphic novel PDF, Fountain screenplay, master MP4 animatic reel.
- **Providers:** OpenAI, Anthropic, Google GenAI, Groq, OpenRouter, and local Ollama / Stable Diffusion — with encrypted key storage and deterministic offline fallback rendering.
- **Audio:** procedural 16-bit 44.1 kHz score and foley synthesis (6 score + 5 SFX presets).
- **Governance:** boot-time integrity verification of the Prime Directive and the 10 Laws, with per-request audit logging.
- **Desktop:** one-click launchers, NLE keyboard navigation (J-K-L, 1–9 studio switcher), graceful shutdown.

---

## 4. What Changed in 3.3.0

This release is a **stability and integrity release**, not a feature release. It exists because a full audit found that v3.2.0 **could not be installed or started from a clean checkout**.

| Fix | Impact |
|---|---|
| Completed and pinned `backend/requirements.txt`; added `requirements-dev.txt` | Clean installs now boot. `opencv-python-headless`, `numpy`, `PyMuPDF`, `pypdf` were imported but never declared. |
| Replaced `google-generativeai` with `google-genai` | The provider uses the new SDK; the old package made `import main` fail outright. |
| Path-traversal containment on sample-script loading | Closed a **confirmed arbitrary file read** exploit. |
| Restored ESLint configuration | `npm run lint` had been failing with "couldn't find a configuration file". |
| Single-sourced `APP_VERSION` | OpenAPI had been advertising `2.0.0` while `/health` reported `3.2.0`. |
| Repaired GitHub Actions CI | The pipeline could not install dependencies and therefore could not have been passing. |
| +13 regression tests | Locks in the traversal fix, the dependency contract, and version consistency. |
| Full documentation rewrite | CHANGELOG, ROADMAP, API_REFERENCE (now all 60 endpoints), PRD, README, plus this status doc. |

Full detail: [CHANGELOG.md](./CHANGELOG.md).

---

## 5. Known Limitations

Be aware of these before shipping to end users:

1. **Loopback only.** The API has no authentication. `POST /system/shutdown` will terminate the process for anyone who can reach it. Never bind CineMatrix to a non-loopback interface.
2. **Encryption fails open.** If `STORYBOARD_SECRET_KEY` is unset, a fixed development secret is used; if encryption raises, the API key is stored in plaintext. Set `STORYBOARD_SECRET_KEY` explicitly. *(Phase 11)*
3. **Uploads are only partially bounded.** A 20 MB cap applies after parsing, with no extension allow-list and no archive decompression limits. *(Phase 11)*
4. **Long generation jobs run inside the HTTP request.** Large batch renders can time out and leave partial state; there is no resumable job tracking. *(Phase 12)*
5. **No frontend tests.** TypeScript compilation is the only automated frontend check. *(Phase 13)*
6. **Windows-first desktop launcher.** Browser discovery uses hardcoded Windows paths. *(Phase 14)*
7. **GPU contention.** Running local Whisper/TTS alongside local diffusion on a single GPU can exhaust VRAM. No automatic offload scheduling yet. *(Phase 14)*
8. **Dead modules.** `memory_service.py`, `feedback_engine.py`, and `prompt_optimizer.py` are not wired into the application. *(Phase 14)*

---

## 6. Verification Commands

Reproduce the status above from a clean checkout:

```bash
# Backend — install, boot check, tests
python -m venv .venv
.venv\Scripts\pip install -r backend/requirements-dev.txt
cd backend && python -c "import main; print(main.APP_VERSION, len(main.app.routes))"
cd .. && python -m pytest backend/tests -q          # expect: 117 passed

# Frontend — lint, typecheck, production build
cd frontend
npm ci
npm run lint        # expect: exit 0
npm run typecheck   # expect: exit 0
npm run build       # expect: exit 0
```

Last full verification run: **2026-10-14** — all green.

---

## 7. Release Readiness

| Gate | Required for | Status |
|---|---|---|
| Installs and boots from clean checkout | Any release | ✅ Pass |
| Full test suite green | Any release | ✅ Pass |
| CI green on `main` | Any release | ✅ Pass |
| No open critical defects | Creator beta | ✅ Pass |
| No open high defects | Public commercial | ❌ H-2 open (Phase 11) |
| Upload hardening complete | Public commercial | ❌ Phase 11 |
| Job queue for long renders | Paid tier SLA | ❌ Phase 12 |
| Frontend test coverage | Public commercial | ❌ Phase 13 |
| Cross-platform desktop build | v4.0.0 | ❌ Phase 14 |

**Recommendation:** ship the **creator beta** now. Hold the **$149 commercial launch** until Phase 11 and Phase 12 close.

---

## 8. Next Actions

| # | Action | Phase | Target |
|---|---|---|---|
| 1 | Fail-closed encryption + key migration | 11 | v3.4.0 |
| 2 | Upload allow-list, archive bomb limits, zip-slip guard | 11 | v3.4.0 |
| 3 | Sanitised error envelope with correlation IDs | 11 | v3.4.0 |
| 4 | Move blocking generation off the event loop | 12 | v3.5.0 |
| 5 | Resumable batch jobs with progress polling | 12 | v3.5.0 |
| 6 | Vitest harness; clear 84 lint warnings | 13 | v3.6.0 |
| 7 | Shared typed API client; split oversized components | 13 | v3.6.0 |
| 8 | Cross-platform launcher; remove dead modules | 14 | v4.0.0 |
