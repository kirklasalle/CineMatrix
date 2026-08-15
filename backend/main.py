from typing import Optional, List, Dict, Any, Union
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Request # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from models.schemas import ProjectCreate, ScriptUpload, ProviderConfig # type: ignore
from database.models import init_db, SessionLocal, Project, Script, Scene, Character, StoryboardFrame, ProviderConfiguration # type: ignore
from script_parser import ScriptParser # type: ignore
from storyboard_engine import StoryboardEngine # type: ignore
from providers.openai_provider import OpenAIProvider # type: ignore
from providers.local_provider import LocalProvider # type: ignore
from providers.anthropic_provider import AnthropicProvider # type: ignore
from providers.google_provider import GoogleProvider # type: ignore
from providers.open_router_provider import OpenRouterProvider # type: ignore
from providers.groq_provider import GroqProvider # type: ignore
from logging_config import configure_logging  # type: ignore
from governance import GovernanceEngine  # type: ignore
from knowledge_base import CinematicKnowledgeBase  # type: ignore
from content_agreement import get_agreement, log_acceptance  # type: ignore
from crypto_utils import encrypt_api_key, decrypt_api_key  # type: ignore
from character_library import CharacterLibrary  # type: ignore
import json
import datetime
import uvicorn # type: ignore
import uuid
import os
import httpx # type: ignore
import logging
import time
import io
from parsers.format_detector import detect_format  # type: ignore
from parsers.docx_parser import extract_docx_text  # type: ignore
from parsers.fdx_parser import parse_fdx  # type: ignore
from parsers.fountain_parser import parse_fountain  # type: ignore
from style_vault import list_styles  # type: ignore
from export_service import ExportService  # type: ignore
from video_engine import VideoEngine, MOTION_PRESETS  # type: ignore
from story_doctor import StoryDoctor, BLAKE_SNYDER_BEATS  # type: ignore
from table_read_orchestrator import TableReadOrchestrator  # type: ignore
from graphic_novel_engine import GraphicNovelEngine, PANEL_LAYOUT_PRESETS  # type: ignore
from audio_scoring_engine import AudioScoringEngine, SCORE_PRESETS, FOLEY_PRESETS  # type: ignore
from examples_service import list_examples, get_example_by_id, read_example_content, EXAMPLES_BASE_DIR  # type: ignore
from parsers.comic_parser import parse_cbz  # type: ignore
from parsers.epub_parser import parse_epub  # type: ignore
import asyncio
from fastapi.staticfiles import StaticFiles  # type: ignore

# ── Logging: verbose trace to /logs ──────────────────────────────────────────
configure_logging("storyboard")
logger = logging.getLogger("storyboard-api")

# ── Governance: boot verification of Prime Directive + 10 Laws ───────────────
GovernanceEngine.boot_verify()

# ── Database initialization ───────────────────────────────────────────────────
init_db()

# ── Cinematic Knowledge Base (Second Brain) ───────────────────────────────────
knowledge_base = CinematicKnowledgeBase(SessionLocal)

# ── Character Library (Growing Archetype Database) ────────────────────────────
character_library = CharacterLibrary(SessionLocal)

app = FastAPI(
    title="Storyboard AI API",
    description=(
        "Storyboard AI — governed by the PRISM Agentic Prime Directive, "
        "the Sacred Covenant, and the Permanent Active Directives (The 10 Laws). "
        "Author: Kirk LaSalle."
    ),
    version="2.0.0",
)

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(os.path.join(STATIC_DIR, "videos"), exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    origin = request.headers.get("origin", "*")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers={
            "Access-Control-Allow-Origin": origin if origin else "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    client_host = request.client.host if request.client else "unknown"
    logger.debug(
        f"▶ REQUEST  {request.method} {request.url.path} "
        f"client={client_host} "
        f"query={dict(request.query_params) or '{}'}"
    )
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        logger.info(
            f"◀ RESPONSE {request.method} {request.url.path} "
            f"status={response.status_code} duration={duration:.3f}s"
        )
        GovernanceEngine.audit_api_call(request.url.path)
        return response
    except Exception as exc:
        duration = time.time() - start_time
        logger.error(
            f"◀ ERROR    {request.method} {request.url.path} "
            f"error={exc} duration={duration:.3f}s"
        )
        raise exc


@app.post("/system/shutdown")
async def shutdown_server():
    """
    Gracefully shuts down the Storyboard AI server process.
    """
    logger.info("SYSTEM: Graceful shutdown initiated via API.")
    GovernanceEngine.audit_api_call("/system/shutdown")
    
    async def _delayed_shutdown():
        await asyncio.sleep(0.5)
        logger.info("SYSTEM: Terminating server process.")
        os._exit(0)
        
    asyncio.create_task(_delayed_shutdown())
    return {"status": "success", "message": "Storyboard AI server is shutting down cleanly."}

@app.get("/examples")
async def get_examples(category: Optional[str] = None):
    """Returns the catalog of all 27 world-class sample scripts."""
    logger.debug(f"API: Examples catalog requested (category={category})")
    return list_examples(category=category)

@app.get("/examples/{category}/{filename}")
async def get_example_preview(category: str, filename: str):
    """Returns the content or preview of a specific sample script."""
    try:
        return read_example_content(category, filename)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Example script '{category}/{filename}' not found.")
    except Exception as e:
        logger.error(f"Error reading example {category}/{filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agreement")
async def get_content_agreement():
    """Returns the full User Content Agreement."""
    return get_agreement()

@app.get("/styles")
async def get_styles():
    """Returns all available storyboard art styles."""
    logger.debug("Fetching storyboard style list")
    return list_styles()

@app.get("/governance")
async def get_governance():
    """Returns the PRISM governance framework — The 10 Laws and directives."""
    logger.info("GOVERNANCE: Governance framework requested")
    return GovernanceEngine.get_governance_summary()

@app.get("/knowledge")
async def get_knowledge(genre: str = None, knowledge_type: str = None, limit: int = 50):
    """Returns entries from the Cinematic Knowledge Base (Second Brain)."""
    logger.debug(f"KB: List request — genre={genre} type={knowledge_type}")
    return knowledge_base.list_entries(genre=genre, knowledge_type=knowledge_type, limit=limit)

@app.get("/knowledge/stats")
async def get_knowledge_stats():
    """Returns statistics about the Cinematic Knowledge Base."""
    return knowledge_base.get_stats()

@app.post("/knowledge/learn")
async def teach_knowledge(entry: dict):
    """Manually add an insight to the Cinematic Knowledge Base."""
    if not entry.get("title") or not entry.get("content"):
        raise HTTPException(status_code=400, detail="title and content are required")
    entry_id = knowledge_base.learn(
        knowledge_type=entry.get("type", "cinematography"),
        title=entry["title"],
        content=entry["content"],
        genre=entry.get("genre", "all"),
        tags=entry.get("tags", []),
        source=entry.get("source", "Manual Entry"),
        confidence=float(entry.get("confidence", 0.8)),
    )
    return {"status": "learned", "id": entry_id}

# ── Character Library Endpoints ───────────────────────────────────────────────

@app.get("/characters/library")
async def get_character_library(role: str = None, genre_type: str = None, limit: int = 100):
    """List archetypes from the global character library."""
    return character_library.list_archetypes(role=role, genre_type=genre_type, limit=limit)

@app.get("/characters/library/stats")
async def get_character_library_stats():
    """Return statistics and taxonomy for the character library."""
    return character_library.get_stats()

@app.get("/characters/library/taxonomy")
async def get_character_taxonomy():
    """Return the complete character type taxonomy (all roles, archetypes, tiers, genre types)."""
    return CharacterLibrary.get_full_taxonomy()

@app.get("/projects/{project_id}/characters")
async def get_project_characters(project_id: str):
    """Return all characters profiled for a project."""
    from database.models import Character  # type: ignore
    db = SessionLocal()
    try:
        chars = db.query(Character).filter(Character.project_id == project_id).all()
        return [
            {
                "id": c.id, "name": c.name, "description": c.description,
                "age_range": c.age_range, "role": c.role, "wardrobe": c.wardrobe,
                "visual_prompt": c.visual_prompt, "voice_id": c.voice_id,
                "voice_description": c.voice_description, "voice_notes": c.voice_notes,
                "first_scene": c.first_scene, "scene_count": c.scene_count,
                "line_count": c.line_count, "is_lead": c.is_lead,
            }
            for c in chars
        ]
    finally:
        db.close()

@app.get("/projects/{project_id}/scenes")
async def get_project_scenes(project_id: str):
    """Return all persisted scenes for a project."""
    from database.models import Scene  # type: ignore
    db = SessionLocal()
    try:
        scenes = db.query(Scene).filter(Scene.project_id == project_id).order_by(Scene.scene_number).all()
        return [
            {
                "id": s.id, "scene_number": s.scene_number, "heading": s.heading,
                "content": s.content, "characters": json.loads(s.characters or "[]"),
            }
            for s in scenes
        ]
    finally:
        db.close()

@app.get("/projects/{project_id}/export/shot-list.csv")
async def export_shot_list(project_id: str):
    """
    Export a professional shot list CSV — the document DPs and ADs use on set.
    Columns: Scene #, Heading, Shot Type, Camera Movement, Lens,
             Lighting, Intensity, Type, Characters, Moment Summary
    """
    from fastapi.responses import Response as _Resp
    import csv as _csv
    import io as _io
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        frames = (
            db.query(StoryboardFrame)
            .filter(StoryboardFrame.project_id == project_id)
            .order_by(StoryboardFrame.scene_number)
            .all()
        )
        output = _io.StringIO()
        writer = _csv.writer(output)
        writer.writerow([
            "Scene #", "Scene Heading", "Shot Type", "Camera Movement", "Lens",
            "Lighting", "Intensity Score", "Intensity Type", "Characters", "Moment Summary"
        ])
        for f in frames:
            chars = ", ".join(json.loads(f.scene_characters or "[]"))
            writer.writerow([
                f.scene_number, f.heading or "", f.shot_type or "",
                f.camera_movement or "", f.lens or "", f.lighting or "",
                f"{f.intensity_score:.1f}" if f.intensity_score else "",
                f.intensity_type or "", chars, f.moment_summary or "",
            ])
        csv_content = output.getvalue()
        filename = f"shot-list-{(project.name or project_id[:8]).replace(' ', '-').lower()}.csv"
        logger.info(f"EXPORT: Shot list generated for project {project_id} ({len(frames)} frames)")
        return _Resp(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
        )
    finally:
        db.close()

@app.get("/projects/{project_id}/export/script.fountain")
async def export_fountain(project_id: str):
    """
    Export a project's scenes back to valid Fountain format (round-trip).
    Reconstructs a clean .fountain file from persisted scene data.
    """
    from fastapi.responses import Response as _Resp
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        scenes = (
            db.query(Scene)
            .filter(Scene.project_id == project_id)
            .order_by(Scene.scene_number)
            .all()
        )
        if not scenes:
            raise HTTPException(status_code=404, detail="No scenes found. Run analysis first.")

        lines = [
            f"Title: {project.name}",
            f"Author: Storyboard AI Export",
            f"Draft date: {datetime.date.today().isoformat()}",
            "",
            "",
        ]

        for scene in scenes:
            lines.append(scene.heading or f"SCENE {scene.scene_number}")
            lines.append("")
            if scene.content:
                for para in (scene.content or "").split(". "):
                    para = para.strip()
                    if para:
                        lines.append(para + ("." if not para.endswith(".") else ""))
            chars = json.loads(scene.characters or "[]")
            for char in chars:
                lines.append("")
                lines.append(char)
                lines.append("(dialogue)")
            lines.append("")

        fountain_content = "\n".join(lines)
        proj_slug = (project.name or project_id[:8]).replace(" ", "-").lower()
        filename = f"{proj_slug}.fountain"
        logger.info(f"EXPORT: Fountain export for project {project_id} ({len(scenes)} scenes)")
        return _Resp(
            content=fountain_content,
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
        )
    finally:
        db.close()

@app.get("/projects/{project_id}/export/storyboard.pdf")
async def export_storyboard_pdf(project_id: str):
    """
    Export the complete project as an Oscar-grade Landscape PDF Presentation Deck.
    Includes full 16:9 visual frames, shot types, camera specs, lighting setups,
    dialogue excerpts, and director notes.
    """
    from fastapi.responses import Response as _Resp
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        frames = (
            db.query(StoryboardFrame)
            .filter(StoryboardFrame.project_id == project_id)
            .order_by(StoryboardFrame.scene_number)
            .all()
        )
        if not frames:
            raise HTTPException(status_code=404, detail="No storyboard frames found. Run analysis first.")

        script = db.query(Script).filter(Script.project_id == project_id).order_by(Script.version.desc()).first()
        script_format = script.script_format if script else "Screenplay"

        config = db.query(ProviderConfiguration).first()
        storyboard_style = config.storyboard_style if config and config.storyboard_style else "Oscar Prestige"

        frame_dicts = [
            {
                "scene_number": f.scene_number,
                "heading": f.heading,
                "description": f.description,
                "image_path": f.image_path,
                "intensity_score": f.intensity_score,
                "intensity_type": f.intensity_type,
                "moment_summary": f.moment_summary,
                "shot_type": f.shot_type,
                "camera_movement": f.camera_movement,
                "lens": f.lens,
                "lighting": f.lighting,
                "scene_characters": f.scene_characters,
            }
            for f in frames
        ]

        pdf_bytes = ExportService.generate_pdf_bytes(
            project_name=project.name or "Storyboard Project",
            frames=frame_dicts,
            script_format=script_format,
            storyboard_style=storyboard_style,
        )

        proj_slug = (project.name or project_id[:8]).replace(" ", "-").lower()
        filename = f"storyboard-{proj_slug}.pdf"
        logger.info(f"EXPORT: Generated PDF presentation for project {project_id} ({len(frames)} frames)")
        return _Resp(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
        )
    finally:
        db.close()

@app.get("/projects/{project_id}/export/images.zip")
async def export_images_zip(project_id: str):
    """
    Export all rendered storyboard frames and formatted shot-list CSV inside a ZIP archive.
    """
    from fastapi.responses import Response as _Resp
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        frames = (
            db.query(StoryboardFrame)
            .filter(StoryboardFrame.project_id == project_id)
            .order_by(StoryboardFrame.scene_number)
            .all()
        )
        if not frames:
            raise HTTPException(status_code=404, detail="No storyboard frames found. Run analysis first.")

        frame_dicts = [
            {
                "scene_number": f.scene_number,
                "heading": f.heading,
                "description": f.description,
                "image_path": f.image_path,
                "intensity_score": f.intensity_score,
                "intensity_type": f.intensity_type,
                "moment_summary": f.moment_summary,
                "shot_type": f.shot_type,
                "camera_movement": f.camera_movement,
                "lens": f.lens,
                "lighting": f.lighting,
            }
            for f in frames
        ]

        zip_bytes = ExportService.generate_zip_bytes(
            project_name=project.name or "Storyboard Project",
            frames=frame_dicts,
        )

        proj_slug = (project.name or project_id[:8]).replace(" ", "-").lower()
        filename = f"storyboard-{proj_slug}-images.zip"
        logger.info(f"EXPORT: Generated image ZIP bundle for project {project_id} ({len(frames)} frames)")
        return _Resp(
            content=zip_bytes,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
        )
    finally:
        db.close()

@app.get("/projects/{project_id}/export/storyboard.cbz")
async def export_comic_cbz(project_id: str):
    """
    Export all storyboard frames packaged as a standard Comic Book Archive (.cbz) with ComicInfo.xml metadata.
    """
    from fastapi.responses import Response as _Resp
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        frames = (
            db.query(StoryboardFrame)
            .filter(StoryboardFrame.project_id == project_id)
            .order_by(StoryboardFrame.scene_number)
            .all()
        )
        if not frames:
            raise HTTPException(status_code=404, detail="No storyboard frames found. Run analysis first.")

        frame_dicts = [
            {
                "scene_number": f.scene_number,
                "heading": f.heading,
                "description": f.description,
                "image_path": f.image_path,
                "moment_summary": f.moment_summary,
            }
            for f in frames
        ]

        cbz_bytes = ExportService.generate_cbz_bytes(
            project_name=project.name or "Storyboard Graphic Novel",
            frames=frame_dicts,
        )

        proj_slug = (project.name or project_id[:8]).replace(" ", "-").lower()
        filename = f"graphic-novel-{proj_slug}.cbz"
        logger.info(f"EXPORT: Generated CBZ comic archive for project {project_id} ({len(frames)} pages)")
        return _Resp(
            content=cbz_bytes,
            media_type="application/vnd.comicbook+zip",
            headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
        )
    finally:
        db.close()

@app.get("/projects/{project_id}/export/character-lookbook.pdf")
async def export_character_lookbook(project_id: str):
    """
    Export an executive Casting & Character Look-Book PDF deck.
    """
    from fastapi.responses import Response as _Resp
    from database.models import Character as CharModel  # type: ignore
    from concept_art_engine import ConceptArtEngine  # type: ignore
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        chars = (
            db.query(CharModel)
            .filter(CharModel.project_id == project_id)
            .order_by(CharModel.is_lead.desc(), CharModel.scene_count.desc())
            .all()
        )
        if not chars:
            raise HTTPException(status_code=404, detail="No characters found for look-book.")

        char_dicts = [
            {
                "name": c.name,
                "role": c.role,
                "description": c.description,
                "wardrobe": c.wardrobe,
                "voice_id": c.voice_id,
                "is_lead": c.is_lead,
                "visual_prompt": c.visual_prompt,
            }
            for c in chars
        ]

        pdf_bytes = ConceptArtEngine.generate_lookbook_pdf(
            project_name=project.name or "Character Look-Book",
            characters=char_dicts,
        )

        proj_slug = (project.name or project_id[:8]).replace(" ", "-").lower()
        filename = f"character-lookbook-{proj_slug}.pdf"
        logger.info(f"EXPORT: Generated Character Look-Book PDF for project {project_id} ({len(chars)} characters)")
        return _Resp(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
        )
    finally:
        db.close()

# ── Cinematic Audio Scoring & Foley Endpoints (Phase B) ──────────────────────

@app.get("/audio/score-presets")
async def get_audio_score_presets():
    """Returns available procedural cinematic soundtrack score presets."""
    return {
        "presets": [
            {"id": k, **v} for k, v in SCORE_PRESETS.items()
        ]
    }

@app.get("/audio/sfx-presets")
async def get_audio_sfx_presets():
    """Returns available procedural foley sound effects presets."""
    return {
        "presets": [
            {"id": k, **v} for k, v in FOLEY_PRESETS.items()
        ]
    }

@app.post("/audio/score/generate")
async def generate_score_track(body: dict):
    """
    Synthesize a procedural background soundtrack track (WAV audio base64).
    Body: {"preset": "cinematic_epic", "duration": 12.0}
    """
    preset = body.get("preset", "cinematic_epic")
    duration = float(body.get("duration", 12.0))
    
    wav_bytes = AudioScoringEngine.generate_score_track(preset_key=preset, duration_seconds=duration)
    b64_audio = base64.b64encode(wav_bytes).decode("utf-8")

    return {
        "status": "success",
        "preset": preset,
        "duration": duration,
        "audio_base64": b64_audio,
    }

@app.post("/audio/sfx/generate")
async def generate_foley_track(body: dict):
    """
    Synthesize a procedural foley sound effect (WAV audio base64).
    Body: {"sfx": "cinematic_boom"}
    """
    sfx = body.get("sfx", "cinematic_boom")
    wav_bytes = AudioScoringEngine.generate_foley_sfx(sfx_key=sfx)
    b64_audio = base64.b64encode(wav_bytes).decode("utf-8")

    return {
        "status": "success",
        "sfx": sfx,
        "audio_base64": b64_audio,
    }

# ── Graphic Novel Creation Studio Endpoints (Phase 9) ───────────────────────

@app.get("/graphic-novel/layouts")
async def get_graphic_novel_layouts():
    """Returns available graphic novel panel layout presets."""
    return {
        "layouts": [
            {"id": k, **v} for k, v in PANEL_LAYOUT_PRESETS.items()
        ]
    }

@app.get("/projects/{project_id}/graphic-novel/pages")
async def get_project_graphic_novel_pages(project_id: str, layout: str = "4_quadrant"):
    """
    Organizes screenplay scenes into formatted graphic novel pages according to selected layout.
    """
    db = SessionLocal()
    try:
        scenes = (
            db.query(Scene)
            .filter(Scene.project_id == project_id)
            .order_by(Scene.scene_number)
            .all()
        )
        frames = (
            db.query(StoryboardFrame)
            .filter(StoryboardFrame.project_id == project_id)
            .order_by(StoryboardFrame.scene_number)
            .all()
        )

        scene_dicts = [{"scene_number": s.scene_number, "heading": s.heading, "content": s.content} for s in scenes]
        frame_dicts = [
            {
                "scene_number": f.scene_number,
                "description": f.description,
                "moment_summary": f.moment_summary,
                "image_path": f.image_path,
            }
            for f in frames
        ]

        pages = GraphicNovelEngine.paginate_scenes(scene_dicts, frame_dicts, layout_preset=layout)
        return {
            "project_id": project_id,
            "layout": layout,
            "page_count": len(pages),
            "pages": pages,
        }
    finally:
        db.close()

@app.get("/projects/{project_id}/export/graphic-novel-print.pdf")
async def export_graphic_novel_print_pdf(project_id: str, layout: str = "4_quadrant"):
    """
    Export a 300 DPI high-resolution Graphic Novel Print Edition PDF.
    """
    from fastapi.responses import Response as _Resp
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        scenes = db.query(Scene).filter(Scene.project_id == project_id).order_by(Scene.scene_number).all()
        frames = db.query(StoryboardFrame).filter(StoryboardFrame.project_id == project_id).order_by(StoryboardFrame.scene_number).all()

        scene_dicts = [{"scene_number": s.scene_number, "heading": s.heading, "content": s.content} for s in scenes]
        frame_dicts = [
            {
                "scene_number": f.scene_number,
                "description": f.description,
                "moment_summary": f.moment_summary,
                "image_path": f.image_path,
            }
            for f in frames
        ]

        pages = GraphicNovelEngine.paginate_scenes(scene_dicts, frame_dicts, layout_preset=layout)
        pdf_bytes = GraphicNovelEngine.generate_print_pdf(
            project_name=project.name or "Graphic Novel",
            pages=pages,
        )

        proj_slug = (project.name or project_id[:8]).replace(" ", "-").lower()
        filename = f"graphic-novel-print-{proj_slug}.pdf"
        logger.info(f"EXPORT: Generated Graphic Novel Print PDF for project {project_id} ({len(pages)} pages)")
        return _Resp(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
        )
    finally:
        db.close()

@app.get("/video/presets")
async def get_video_presets():
    """Returns available camera motion animatic presets."""
    return {
        "presets": [
            {"id": k, **v} for k, v in MOTION_PRESETS.items()
        ]
    }

@app.get("/projects/{project_id}/export/animatic-reel.mp4")
async def export_animatic_reel(project_id: str):
    """
    Compile and export a master cinematic animatic video reel (.mp4).
    Stitches all scene motion animatics with director title cards and lower third slates.
    """
    from fastapi.responses import Response as _Resp
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        frames = (
            db.query(StoryboardFrame)
            .filter(StoryboardFrame.project_id == project_id)
            .order_by(StoryboardFrame.scene_number)
            .all()
        )
        if not frames:
            raise HTTPException(status_code=404, detail="No storyboard frames found to compile animatic reel.")

        frame_dicts = [
            {
                "scene_number": f.scene_number,
                "heading": f.heading,
                "shot_type": f.shot_type,
                "image_path": f.image_path,
                "motion_preset": f.motion_preset or "dolly_in",
            }
            for f in frames
        ]

        video_bytes = VideoEngine.compile_master_reel(
            project_name=project.name or "Storyboard Project",
            frames=frame_dicts,
        )

        proj_slug = (project.name or project_id[:8]).replace(" ", "-").lower()
        filename = f"animatic-reel-{proj_slug}.mp4"
        logger.info(f"EXPORT: Generated animatic video reel for project {project_id} ({len(frames)} scenes)")
        return _Resp(
            content=video_bytes,
            media_type="video/mp4",
            headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
        )
    finally:
        db.close()

# ── Story Doctor & Beat Sheet Analysis Endpoints (Phase 5) ───────────────────

@app.get("/projects/{project_id}/analysis/beat-sheet")
async def get_project_beat_sheet(project_id: str):
    """Returns Blake Snyder 15-beat screenplay structural breakdown."""
    db = SessionLocal()
    try:
        scenes = (
            db.query(Scene)
            .filter(Scene.project_id == project_id)
            .order_by(Scene.scene_number)
            .all()
        )
        frames = (
            db.query(StoryboardFrame)
            .filter(StoryboardFrame.project_id == project_id)
            .order_by(StoryboardFrame.scene_number)
            .all()
        )

        scene_dicts = [{"scene_number": s.scene_number, "heading": s.heading, "content": s.content} for s in scenes]
        frame_dicts = [
            {
                "scene_number": f.scene_number,
                "intensity_score": f.intensity_score,
                "intensity_type": f.intensity_type,
                "moment_summary": f.moment_summary,
                "image_path": f.image_path,
            }
            for f in frames
        ]

        result = StoryDoctor.analyze_beat_sheet(scene_dicts, frame_dicts)
        return result
    finally:
        db.close()

@app.get("/projects/{project_id}/analysis/narrative-arc")
async def get_project_narrative_arc(project_id: str):
    """Returns time-series narrative tension and pacing arc across scenes."""
    db = SessionLocal()
    try:
        scenes = (
            db.query(Scene)
            .filter(Scene.project_id == project_id)
            .order_by(Scene.scene_number)
            .all()
        )
        frames = (
            db.query(StoryboardFrame)
            .filter(StoryboardFrame.project_id == project_id)
            .order_by(StoryboardFrame.scene_number)
            .all()
        )

        scene_dicts = [{"scene_number": s.scene_number, "heading": s.heading} for s in scenes]
        frame_dicts = [{"scene_number": f.scene_number, "intensity_score": f.intensity_score} for f in frames]

        curve = StoryDoctor.calculate_narrative_arc(scene_dicts, frame_dicts)
        return {"project_id": project_id, "arc": curve}
    finally:
        db.close()

@app.get("/projects/{project_id}/analysis/coverage")
async def get_project_coverage(project_id: str):
    """Returns executive script coverage analysis report."""
    from database.models import Character as CharModel  # type: ignore
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        scenes = db.query(Scene).filter(Scene.project_id == project_id).order_by(Scene.scene_number).all()
        frames = db.query(StoryboardFrame).filter(StoryboardFrame.project_id == project_id).order_by(StoryboardFrame.scene_number).all()
        chars = db.query(CharModel).filter(CharModel.project_id == project_id).all()

        scene_dicts = [{"scene_number": s.scene_number, "heading": s.heading, "content": s.content} for s in scenes]
        frame_dicts = [{"scene_number": f.scene_number, "intensity_score": f.intensity_score} for f in frames]
        char_dicts = [{"name": c.name, "is_lead": c.is_lead} for c in chars]

        coverage = StoryDoctor.generate_coverage_summary(
            project_name=project.name or "Screenplay Project",
            scenes=scene_dicts,
            frames=frame_dicts,
            characters=char_dicts,
        )
        return coverage
    finally:
        db.close()

@app.post("/projects/{project_id}/analysis/story-doctor/chat")
async def story_doctor_chat(project_id: str, body: dict):
    """
    Context-aware Story Doctor assistant for scene punch-up, dramatic advice, and structure polish.
    """
    message = body.get("message", "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        scenes = db.query(Scene).filter(Scene.project_id == project_id).all()
        config = db.query(ProviderConfiguration).first()

        provider = get_provider(config) if config else None
        
        # If provider configured, ask the LLM with context
        prompt = (
            f"You are an Oscar-winning Script Doctor and dramaturg working on '{project.name if project else 'the screenplay'}'. "
            f"The screenplay has {len(scenes)} scenes. "
            f"Writer's Question: {message}\n\n"
            "Provide insightful, craft-grounded dramatic guidance. Focus on subtext, conflict escalation, and character motivation. Keep response punchy and actionable."
        )

        if provider:
            response_text = await provider.generate_text(prompt, system_prompt="You are a world-class Oscar-winning Screenplay Doctor.")
        else:
            response_text = (
                f"**Story Doctor Insight for '{project.name if project else 'your screenplay'}':**\n\n"
                f"Regarding *\"{message}\"*, consider heightening the scene's central subtext. "
                "Ensure the protagonist's internal need collides directly with their external goal in this beat. "
                "Every line of dialogue should carry hidden intention rather than surface exposition."
            )

        return {
            "status": "success",
            "reply": response_text,
            "project_id": project_id,
        }
    finally:
        db.close()

@app.get("/projects/{project_id}/readthrough/cast")
async def get_readthrough_cast(project_id: str):
    """
    Return the read-through cast list — all characters with their assigned
    TTS voice profiles. The foundation for virtual read-throughs.
    """
    from database.models import Character as CharModel  # type: ignore
    from character_library import VOICE_PROFILES
    db = SessionLocal()
    try:
        chars = (
            db.query(CharModel)
            .filter(CharModel.project_id == project_id)
            .order_by(CharModel.is_lead.desc(), CharModel.scene_count.desc())
            .all()
        )
        cast = []
        for c in chars:
            voice_profile = VOICE_PROFILES.get(c.voice_id or "alloy", {})
            cast.append({
                "name": c.name,
                "role": c.role,
                "voice_id": c.voice_id or "alloy",
                "voice_provider": c.voice_provider or "openai",
                "voice_description": c.voice_description or "",
                "voice_quality": voice_profile.get("quality", ""),
                "voice_best_for": voice_profile.get("best_for", ""),
                "is_lead": c.is_lead,
                "scene_count": c.scene_count,
                "visual_prompt": c.visual_prompt or "",
                "tts_ready": bool(c.voice_id),
            })
        return {
            "project_id": project_id,
            "cast_count": len(cast),
            "cast": cast,
            "supported_providers": ["openai", "elevenlabs"],
            "openai_voices": list(VOICE_PROFILES.keys()),
            "note": (
                "TTS generation uses the voice_id assigned to each character. "
                "OpenAI TTS: provide OPENAI_API_KEY. "
                "Full audio generation endpoint: POST /projects/{id}/readthrough/generate"
            ),
        }
    finally:
        db.close()

@app.get("/projects/{project_id}/readthrough/scene/{scene_number}")
async def get_scene_readthrough(project_id: str, scene_number: int):
    """
    Returns structured dialogue cues, character voice assignments,
    and synchronized timeline for a specific screenplay scene.
    """
    from database.models import Character as CharModel  # type: ignore
    db = SessionLocal()
    try:
        scene = (
            db.query(Scene)
            .filter(Scene.project_id == project_id, Scene.scene_number == scene_number)
            .first()
        )
        if not scene:
            raise HTTPException(status_code=404, detail="Scene not found")

        chars = db.query(CharModel).filter(CharModel.project_id == project_id).all()
        char_voice_map = {c.name.upper(): c.voice_id or "alloy" for c in chars}

        cues = TableReadOrchestrator.extract_dialogue_cues(scene.content or "")
        timeline = TableReadOrchestrator.generate_timeline_timestamps(cues)

        for t in timeline:
            char_name = t["character"].upper()
            if char_name == "NARRATOR":
                t["voice_id"] = "alloy"
            else:
                t["voice_id"] = char_voice_map.get(char_name, "alloy")

        return {
            "project_id": project_id,
            "scene_number": scene_number,
            "heading": scene.heading,
            "cues": timeline,
            "total_duration": timeline[-1]["end_time"] if timeline else 0.0,
        }
    finally:
        db.close()

@app.post("/projects/{project_id}/readthrough/generate")
async def generate_readthrough_line(project_id: str, body: dict):
    """
    Generate a TTS audio sample for a single character line.
    Body: {"character_name": "HARRIS", "text": "You were here all night.", "voice_id": "onyx"}
    Returns base64 audio or a provider-specific audio URL.
    """
    character_name = body.get("character_name", "")
    text = body.get("text", "").strip()
    voice_id = body.get("voice_id", "alloy")

    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    db = SessionLocal()
    try:
        config = db.query(ProviderConfiguration).first()
        if not config or config.type != "openai":
            return {
                "status": "unavailable",
                "message": "TTS read-through requires an OpenAI provider configuration.",
                "character": character_name,
                "voice_id": voice_id,
                "text_preview": text[:80],
            }

        from crypto_utils import decrypt_api_key  # type: ignore
        api_key = decrypt_api_key(config.api_key or "")
        if not api_key:
            raise HTTPException(status_code=400, detail="No valid API key configured.")

        import openai as _oai  # type: ignore
        client = _oai.AsyncOpenAI(api_key=api_key)
        response = await client.audio.speech.create(
            model="tts-1",
            voice=voice_id,
            input=text,
        )
        import base64
        audio_b64 = base64.b64encode(response.content).decode("utf-8")
        logger.info(f"TTS: Generated line for '{character_name}' voice={voice_id} ({len(text)} chars)")
        return {
            "status": "success",
            "character": character_name,
            "voice_id": voice_id,
            "audio_base64": audio_b64,
            "audio_format": "mp3",
            "text": text,
        }
    except Exception as e:
        logger.error(f"TTS: Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/characters/audition")
async def audition_voice(body: dict):
    """
    Generate a quick TTS voice audition sample for any voice ID.
    Body: {"voice_id": "onyx", "text": "...", "character_name": "..."}
    """
    character_name = body.get("character_name", "Character")
    voice_id = body.get("voice_id", "alloy")
    text = body.get("text", "").strip() or "Every element is used because the story demands it."

    db = SessionLocal()
    try:
        config = db.query(ProviderConfiguration).first()
        from crypto_utils import decrypt_api_key  # type: ignore
        api_key = decrypt_api_key(config.api_key or "") if config else ""

        if not config or not api_key:
            return {
                "status": "unavailable",
                "message": "Auditioning requires a configured OpenAI API Key in Configuration.",
                "voice_id": voice_id,
                "character": character_name,
            }

        import openai as _oai  # type: ignore
        client = _oai.AsyncOpenAI(api_key=api_key)
        response = await client.audio.speech.create(
            model="tts-1",
            voice=voice_id,
            input=text,
        )
        import base64
        audio_b64 = base64.b64encode(response.content).decode("utf-8")
        logger.info(f"AUDITION: Generated voice sample for '{character_name}' voice={voice_id}")
        return {
            "status": "success",
            "character": character_name,
            "voice_id": voice_id,
            "audio_base64": audio_b64,
            "audio_format": "mp3",
            "text": text,
        }
    except Exception as e:
        logger.error(f"AUDITION: Failed: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

@app.patch("/projects/{project_id}/characters/{character_id}")
async def update_character(project_id: str, character_id: str, body: dict):
    """Update character details such as assigned voice, wardrobe, role, or visual prompt."""
    from database.models import Character as CharModel  # type: ignore
    db = SessionLocal()
    try:
        char = db.query(CharModel).filter(CharModel.project_id == project_id, CharModel.id == character_id).first()
        if not char:
            raise HTTPException(status_code=404, detail="Character not found")

        if "voice_id" in body:
            char.voice_id = body["voice_id"]
        if "role" in body:
            char.role = body["role"]
        if "wardrobe" in body:
            char.wardrobe = body["wardrobe"]
        if "visual_prompt" in body:
            char.visual_prompt = body["visual_prompt"]
        if "description" in body:
            char.description = body["description"]

        db.commit()
        db.refresh(char)
        logger.info(f"CHARACTER: Updated {char.name} in project {project_id}")
        return {
            "id": char.id,
            "name": char.name,
            "role": char.role,
            "voice_id": char.voice_id,
            "wardrobe": char.wardrobe,
            "visual_prompt": char.visual_prompt,
            "description": char.description,
        }
    finally:
        db.close()

@app.get("/providers/local/models")
async def get_local_models(base_url: str = "http://127.0.0.1:11434"):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/tags")
            if response.status_code == 200:
                return response.json().get("models", [])
        return []
    except Exception as e:
        return []


def _get_persisted_provider_config(db):
    config = db.query(ProviderConfiguration).filter(ProviderConfiguration.id == "default").first()
    if config:
        return config
    return db.query(ProviderConfiguration).first()


def _merge_with_persisted_config(config: ProviderConfig) -> ProviderConfig:
    """Fill missing fields from persisted config, scoped to the same provider type."""
    db = SessionLocal()
    try:
        saved = _get_persisted_provider_config(db)
        if not saved:
            return config

        if config.type and saved.type and config.type != saved.type:
            return config

        return config.copy(update={
            "type": config.type or saved.type,
            "api_key": config.api_key if config.api_key else (saved.api_key or ""),
            "base_url": config.base_url or saved.base_url,
            "model_name": config.model_name or saved.model_name,
            "storyboard_style": config.storyboard_style or saved.storyboard_style or "oscar_prestige",
        })
    finally:
        db.close()

def get_provider(config: ProviderConfig):
    # Decrypt API key at use-time (transparent for both encrypted and legacy plaintext)
    api_key = decrypt_api_key(config.api_key)
    if config.type == "openai":
        return OpenAIProvider(api_key=api_key, base_url=config.base_url, model_name=config.model_name or "gpt-4o")
    elif config.type == "anthropic":
        return AnthropicProvider(api_key=api_key, model_name=config.model_name or "claude-3-5-sonnet-20240620", base_url=config.base_url)
    elif config.type == "google":
        return GoogleProvider(api_key=api_key, model_name=config.model_name or "gemini-1.5-flash")
    elif config.type == "openrouter":
        return OpenRouterProvider(api_key=api_key, model_name=config.model_name or "meta-llama/llama-3.1-8b-instruct:free", base_url=config.base_url)
    elif config.type == "groq":
        return GroqProvider(api_key=api_key, model_name=config.model_name or "llama-3.1-70b-versatile", base_url=config.base_url)
    elif config.type == "local":
        return LocalProvider(base_url=config.base_url, model_name=config.model_name or "llama3")
    else:
        raise ValueError(f"Unknown provider type: {config.type}")

@app.get("/providers/image-status")
async def get_image_status():
    """Returns the current image generation readiness status."""
    db = SessionLocal()
    try:
        config = _get_persisted_provider_config(db)
        if not config:
            return {
                "ready": True,
                "provider": "Pollinations.ai",
                "model": "Community Free",
                "tier": "free",
                "message": "No provider configured. Free Pollinations.ai will be used.",
                "models_available": [
                    {"name": "Pollinations.ai", "status": "ready", "tier": "free"}
                ]
            }
        
        provider_name = config.type or "unknown"
        model_name = config.model_name or "default"
        
        # Map provider types to their image model chains
        image_chains = {
            "openai": [
                {"name": "gpt-image-1", "tier": "paid"},
                {"name": "dall-e-3", "tier": "paid"},
                {"name": "dall-e-2", "tier": "paid"},
            ],
            "google": [
                {"name": "imagen-4", "tier": "paid"},
                {"name": "imagen-4-fast", "tier": "paid"},
                {"name": "imagen-3", "tier": "paid"},
                {"name": "imagen-3-fast", "tier": "paid"},
            ],
            "openrouter": [
                {"name": "Provider Image Models", "tier": "paid"},
            ],
            "anthropic": [],
            "groq": [],
            "local": [
                {"name": "Local Image Model", "tier": "local"},
            ],
        }
        
        chain = image_chains.get(provider_name, [])
        # Always add Pollinations.ai as the guaranteed fallback
        chain.append({"name": "Pollinations.ai", "tier": "free"})
        
        # Mark all as potentially available, Pollinations as guaranteed
        models_available = []
        for m in chain:
            models_available.append({
                "name": m["name"],
                "status": "ready" if m["tier"] == "free" else "available",
                "tier": m["tier"]
            })
        
        return {
            "ready": True,
            "provider": provider_name.title(),  # type: ignore
            "text_model": model_name,
            "tier": "paid" if chain and chain[0]["tier"] != "free" else "free",
            "message": f"{provider_name.title()} configured with {len(chain)} image model(s). Pollinations.ai fallback guaranteed.",  # type: ignore
            "models_available": models_available
        }
    finally:
        db.close()

@app.get("/providers/config")
async def get_config():
    db = SessionLocal()
    try:
        config = _get_persisted_provider_config(db)
        if not config:
            return None

        # Never send encrypted API material to the frontend.
        return {
            "id": config.id,
            "type": config.type,
            "base_url": config.base_url,
            "model_name": config.model_name,
            "storyboard_style": config.storyboard_style or "oscar_prestige",
            "api_key": "",
            "has_api_key": bool(config.api_key),
        }
    finally:
        db.close()

@app.post("/providers/models")
async def get_provider_models(config: ProviderConfig):
    try:
        resolved_config = _merge_with_persisted_config(config)
        provider = get_provider(resolved_config)
        models = await provider.list_models()
        return models
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/providers/test")
async def test_provider(config: ProviderConfig):
    # Perform the test
    test_result = {"status": "error", "message": "Unknown provider type"}
    start_time = time.time()
    try:
        logger.info(f"Testing provider: {config.type}")
        resolved_config = _merge_with_persisted_config(config)
        provider = get_provider(resolved_config)
        # verify_connection can now return a dict with status and message
        result = await provider.verify_connection()
        duration = time.time() - start_time
        
        if isinstance(result, dict) and result.get("status") == "success":
            test_result = {"status": "success", "message": result.get("message", "Connection successful"), "duration": f"{duration:.2f}s"}
            logger.info(f"Provider {config.type} test SUCCESS ({duration:.2f}s)")
        elif isinstance(result, bool) and result:
            test_result = {"status": "success", "message": "Connection successful", "duration": f"{duration:.2f}s"}
            logger.info(f"Provider {config.type} test SUCCESS ({duration:.2f}s)")
        else:
            error_msg = result.get("message") if isinstance(result, dict) else "Connection failed. Please check your API Key and Endpoint."
            test_result = {"status": "error", "message": error_msg, "duration": f"{duration:.2f}s"}
            logger.warning(f"Provider {config.type} test FAILED: {error_msg} ({duration:.2f}s)")
    except Exception as e:
        duration = time.time() - start_time
        test_result = {"status": "error", "message": str(e), "duration": f"{duration:.2f}s"}
        logger.error(f"Provider {config.type} test ERROR: {e} ({duration:.2f}s)")

    return test_result

@app.post("/providers/save")
async def save_config(config: ProviderConfig):
    db = SessionLocal()
    try:
        existing = _get_persisted_provider_config(db)
        submitted_api_key = (config.api_key or "").strip()

        if existing:
            existing.type = config.type
            if submitted_api_key:
                existing.api_key = encrypt_api_key(submitted_api_key)
            existing.base_url = config.base_url
            existing.model_name = config.model_name
            existing.storyboard_style = config.storyboard_style or "oscar_prestige"
        else:
            new_config = ProviderConfiguration(
                id="default",
                type=config.type,
                api_key=encrypt_api_key(submitted_api_key),
                base_url=config.base_url,
                model_name=config.model_name,
                storyboard_style=config.storyboard_style or "oscar_prestige",
            )
            db.add(new_config)
        db.commit()
        logger.info(f"Configuration for {config.type} explicitly SAVED")
        return {"status": "success", "message": "Configuration saved"}
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/providers/balance")
async def get_provider_balance(config: ProviderConfig):
    try:
        resolved_config = _merge_with_persisted_config(config)
        provider = get_provider(resolved_config)
        if hasattr(provider, 'get_balance'):
            balance_info = await provider.get_balance()
            return balance_info
        return {"status": "unsupported", "message": f"Balance check not supported for {config.type}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/projects")
async def list_projects():
    """List all saved storyboard projects with summary statistics."""
    db = SessionLocal()
    try:
        projects = db.query(Project).order_by(Project.created_at.desc()).all()
        result = []
        for p in projects:
            scene_count = db.query(Scene).filter(Scene.project_id == p.id).count()
            frame_count = db.query(StoryboardFrame).filter(StoryboardFrame.project_id == p.id).count()
            char_count = db.query(Character).filter(Character.project_id == p.id).count()
            script = db.query(Script).filter(Script.project_id == p.id).order_by(Script.version.desc()).first()
            result.append({
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "scene_count": scene_count,
                "frame_count": frame_count,
                "character_count": char_count,
                "script_filename": script.filename if script else None,
                "script_format": script.script_format if script else None,
            })
        return result
    finally:
        db.close()

@app.post("/projects")
async def create_project(project: ProjectCreate):
    db = SessionLocal()
    try:
        new_project = Project(id=str(uuid.uuid4()), name=project.name, description=project.description)
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        return new_project
    finally:
        db.close()

@app.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project and all associated scripts, scenes, frames, and characters."""
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        db.query(StoryboardFrame).filter(StoryboardFrame.project_id == project_id).delete()
        db.query(Scene).filter(Scene.project_id == project_id).delete()
        db.query(Character).filter(Character.project_id == project_id).delete()
        db.query(Script).filter(Script.project_id == project_id).delete()
        db.delete(project)
        db.commit()
        logger.info(f"API: Project {project_id} deleted with all child records")
        return {"status": "success", "message": f"Project {project_id} deleted"}
    finally:
        db.close()

@app.post("/projects/{project_id}/scripts")
async def upload_script(project_id: str, file: UploadFile = File(...)):
    logger.info(f"API: Received script upload for project {project_id}")

    # Security: enforce file size limit (20 MB)
    MAX_SIZE = 20 * 1024 * 1024
    file_bytes = await file.read(MAX_SIZE + 1)
    if len(file_bytes) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 20 MB.")

    filename = file.filename or "upload.txt"
    fmt = detect_format(filename, file_bytes)
    logger.info(f"API: Detected format '{fmt}' for file '{filename}'")

    # Content Agreement: log irrevocable acceptance upon submission (Law 7 — transparency)
    log_acceptance(project_id, filename)
    GovernanceEngine.audit_data_access(f"script_upload:{filename}", "WRITE")

    content = ""
    script_format = fmt

    if fmt == "pdf":
        try:
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                pages = [p.get_text() or "" for p in doc]
                content = "\n".join(pages)
            except ImportError:
                try:
                    import pdfplumber  # type: ignore
                    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                        pages = [p.extract_text() or "" for p in pdf.pages]
                    content = "\n".join(pages)
                except ImportError:
                    try:
                        import pypdf  # type: ignore
                        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                        pages = [p.extract_text() or "" for p in reader.pages]
                        content = "\n".join(pages)
                    except ImportError:
                        raise HTTPException(
                            status_code=400,
                            detail="PDF parser not installed. Please run: pip install PyMuPDF pdfplumber"
                        )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise HTTPException(status_code=400, detail="Could not extract text from PDF.")

    elif fmt == "docx":
        try:
            content = extract_docx_text(file_bytes)
        except ImportError:
            raise HTTPException(status_code=400, detail="python-docx is required to read .docx files. Run: pip install python-docx")
        except Exception as e:
            logger.error(f"Error parsing DOCX: {e}")
            raise HTTPException(status_code=400, detail="Could not extract text from Word document.")

    elif fmt == "fdx":
        try:
            content = file_bytes.decode("utf-8", errors="replace")
        except Exception as e:
            raise HTTPException(status_code=400, detail="Could not read FDX file.")

    elif fmt == "cbz":
        try:
            res = parse_cbz(file_bytes)
            content = "\n\n".join([f"{s['heading']}\n{s['content']}" for s in res.get("scenes", [])])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not read CBZ comic archive: {e}")

    elif fmt == "epub":
        try:
            res = parse_epub(file_bytes)
            content = "\n\n".join([f"{s['heading']}\n{s['content']}" for s in res.get("scenes", [])])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not read ePub publication: {e}")

    else:
        # text or fountain — decode as UTF-8 with fallback
        try:
            content = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                content = file_bytes.decode("latin-1")
            except Exception as e:
                logger.error(f"Error decoding file: {e}")
                raise HTTPException(status_code=400, detail="Cannot decode file content.")

    if not content.strip():
        raise HTTPException(status_code=400, detail="The uploaded document is empty or unreadable.")

    db = SessionLocal()
    try:
        new_script = Script(
            id=str(uuid.uuid4()),
            project_id=project_id,
            content=content,
            filename=file.filename,
            script_format=script_format,
        )
        db.add(new_script)
        db.commit()
        logger.info(f"API: Script saved successfully. Project ID: {project_id}")
        return {"status": "success", "id": new_script.id, "format": script_format}
    finally:
        db.close()


@app.post("/projects/{project_id}/load-example")
async def load_example_into_project(project_id: str, body: dict):
    """
    Loads one of the 27 sample scripts directly into an existing project.
    Body: {"category": "engines", "filename": "10_story_doctor_15_beats.fountain"}
    """
    category = body.get("category", "engines")
    filename = body.get("filename")
    if not filename:
        raise HTTPException(status_code=400, detail="filename is required")

    file_path = os.path.join(EXAMPLES_BASE_DIR, category, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Example file not found: {category}/{filename}")

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    fmt = detect_format(filename, file_bytes)
    content = ""

    if fmt == "pdf":
        try:
            import fitz
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            pages = [p.get_text() or "" for p in doc]
            content = "\n".join(pages)
        except Exception:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF.")
    elif fmt == "docx":
        content = extract_docx_text(file_bytes)
    elif fmt == "fdx":
        content = file_bytes.decode("utf-8", errors="replace")
    elif fmt == "cbz":
        res = parse_cbz(file_bytes)
        content = "\n\n".join([f"{s['heading']}\n{s['content']}" for s in res.get("scenes", [])])
    elif fmt == "epub":
        res = parse_epub(file_bytes)
        content = "\n\n".join([f"{s['heading']}\n{s['content']}" for s in res.get("scenes", [])])
    else:
        try:
            content = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content = file_bytes.decode("latin-1", errors="replace")

    if not content.strip():
        raise HTTPException(status_code=400, detail="The example script content is empty.")

    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Update project title and description nicely if default
        example_meta = get_example_by_id(filename)
        if example_meta:
            if project.name == "New Storyboard Project" or not project.name or project.name.startswith("Sample"):
                project.name = example_meta["title"]
                project.description = example_meta["description"]

        # Clean prior child records for this project
        db.query(Script).filter(Script.project_id == project_id).delete()
        db.query(Scene).filter(Scene.project_id == project_id).delete()
        db.query(StoryboardFrame).filter(StoryboardFrame.project_id == project_id).delete()
        db.query(Character).filter(Character.project_id == project_id).delete()

        new_script = Script(
            id=str(uuid.uuid4()),
            project_id=project_id,
            content=content,
            filename=filename,
            script_format=fmt,
        )
        db.add(new_script)
        db.commit()

        # Parse scenes
        raw_scenes = []
        if fmt == "fdx":
            raw_scenes = parse_fdx(content)
        elif fmt == "fountain":
            raw_scenes = parse_fountain(content)
        elif fmt == "cbz":
            res = parse_cbz(file_bytes)
            raw_scenes = res.get("scenes", [])
        elif fmt == "epub":
            res = parse_epub(file_bytes)
            raw_scenes = res.get("scenes", [])
        else:
            raw_scenes = ScriptParser.parse(content)

        for idx, scene in enumerate(raw_scenes):
            db_scene = Scene(
                id=str(uuid.uuid4()),
                project_id=project_id,
                script_id=new_script.id,
                scene_number=idx + 1,
                heading=scene.get("heading", f"Scene {idx + 1}"),
                content=scene.get("text", scene.get("content", "")),
                characters=json.dumps(scene.get("characters", [])),
            )
            db.add(db_scene)
        db.commit()

        # ── Auto-generate initial Storyboard Frames & Images for instant visualization ──
        saved_style = example_meta.get("style", "oscar_prestige") if example_meta else "oscar_prestige"
        genre = example_meta.get("genre", "drama") if example_meta else "drama"
        
        # Build default cinematography patterns for example frames
        shot_types = ["Wide Establishing Shot", "Medium Close-Up", "Low Angle Hero Shot", "Over The Shoulder Tracking", "High Angle Extreme Wide", "Dutch Angle Tension"]
        camera_moves = ["Slow Dolly In", "Dynamic Steadicam Tracking", "Handheld Organic Drift", "Slow Pan Right", "Cinematic Crane Move", "Slow-Mo Drift"]
        lenses = ["35mm Anamorphic T1.5", "50mm Prime", "85mm Portrait Prime", "24mm Ultra Wide", "70mm VistaVision", "40mm Cinema Prime"]
        lightings = ["Golden Hour Rim Light with Volumetric Atmosphere", "High-Contrast Chiaroscuro Noir Lighting", "Soft Diffused Natural Daylight", "Dramatic Tungsten & Neon Practical Accent", "Moody Moonlit Ambient with Hard Edge Light", "Direct Sunlight High-Key"]

        from style_vault import get_style as _gs  # type: ignore
        visual_style = _gs(saved_style)

        # Setup engine to generate images
        saved_config = _get_persisted_provider_config(db)
        provider = get_provider(saved_config) if saved_config else get_provider(ProviderConfig(type="local", api_key=""))
        engine = StoryboardEngine(provider, knowledge_base=knowledge_base)

        for idx, scene in enumerate(raw_scenes):
            shot_type = shot_types[idx % len(shot_types)]
            camera_move = camera_moves[idx % len(camera_moves)]
            lens = lenses[idx % len(lenses)]
            lighting = lightings[idx % len(lightings)]
            desc = scene.get("text", scene.get("content", ""))[:280] or f"Cinematic moment in {scene.get('heading', f'Scene {idx+1}')}"
            intensity_score = 7.5 + (idx % 3) * 0.8
            intensity_type = "Action Peak" if idx % 3 == 0 else ("Emotional Peak" if idx % 3 == 1 else "Scene")
            moment_sum = f"Cinematic keyframe for {scene.get('heading', f'Scene {idx+1}')}"
            
            # High-fidelity prompt for 16:9 cinematic storyboard art
            prompt = (
                f"{visual_style.get('prompt_prefix', 'Cinematic production storyboard')}. "
                f"Scene: {desc}. "
                f"Cinematography: {shot_type}, {camera_move}, {lens}, {lighting}. "
                f"{visual_style.get('prompt_suffix', 'award-winning film still, masterwork lighting')}. "
                f"16:9 widescreen aspect ratio."
            )
            image_url = engine._get_pollinations_url(prompt, seed=(idx + 1) * 77 + 13)

            db_frame = StoryboardFrame(
                id=str(uuid.uuid4()),
                project_id=project_id,
                scene_number=idx + 1,
                heading=scene.get("heading", f"Scene {idx + 1}"),
                description=desc,
                intensity_score=intensity_score,
                intensity_type=intensity_type,
                moment_summary=moment_sum,
                shot_type=shot_type,
                camera_movement=camera_move,
                lens=lens,
                lighting=lighting,
                image_path=image_url,
                motion_preset="dolly_in",
                scene_characters=json.dumps(scene.get("characters", [])),
            )
            db.add(db_frame)

        # Pre-populate Character records
        try:
            char_map: Dict[str, List[int]] = {}
            for s_idx, sc in enumerate(raw_scenes):
                for ch in sc.get("characters", []):
                    char_map.setdefault(ch, []).append(s_idx + 1)
            
            fallback_chars = engine._fallback_characters(char_map)
            for cp in fallback_chars:
                db_char = Character(
                    id=str(uuid.uuid4()),
                    project_id=project_id,
                    name=cp["name"],
                    description=cp.get("description", ""),
                    age_range=cp.get("age_range", ""),
                    role=cp.get("role", "supporting"),
                    wardrobe=cp.get("wardrobe", ""),
                    visual_prompt=cp.get("visual_prompt", ""),
                    voice_id=cp.get("voice_id", "alloy"),
                    voice_description=cp.get("voice_description", ""),
                    first_scene=cp.get("first_scene", 1),
                    scene_count=cp.get("scene_count", 0),
                    line_count=cp.get("line_count", 0),
                    is_lead=cp.get("is_lead", False),
                )
                db.add(db_char)
        except Exception as c_err:
            logger.warning(f"API: Example character fallback error: {c_err}")

        db.commit()

        logger.info(f"API: Loaded example '{filename}' into project {project_id} ({len(raw_scenes)} scenes + {len(raw_scenes)} rendered frames)")
        return {
            "status": "success",
            "project_id": project_id,
            "script_id": new_script.id,
            "scene_count": len(raw_scenes),
            "frame_count": len(raw_scenes),
            "title": project.name,
            "format": fmt,
            "style": saved_style,
        }
    finally:
        db.close()


@app.post("/projects/create-with-example")
async def create_project_with_example(body: dict):
    """
    1-click convenience endpoint to create a project and populate it with a sample script.
    Body: {"category": "engines", "filename": "10_story_doctor_15_beats.fountain"}
    """
    category = body.get("category", "engines")
    filename = body.get("filename", "10_story_doctor_15_beats.fountain")

    example_meta = get_example_by_id(filename)
    title = example_meta["title"] if example_meta else "Sample Storyboard Project"
    desc = example_meta["description"] if example_meta else "Loaded from example scripts"

    db = SessionLocal()
    try:
        new_project = Project(
            id=str(uuid.uuid4()),
            name=title,
            description=desc,
        )
        db.add(new_project)
        db.commit()
        project_id = new_project.id
    finally:
        db.close()

    # Load example into the new project
    return await load_example_into_project(project_id, {"category": category, "filename": filename})

@app.post("/projects/{project_id}/generate")
async def generate_storyboard(project_id: str, config: ProviderConfig):
    logger.info(f"API: Starting generation for project {project_id} using {config.type}")
    db = SessionLocal()
    try:
        resolved_config = _merge_with_persisted_config(config)
        script = db.query(Script).filter(Script.project_id == project_id).order_by(Script.version.desc()).first()
        if not script:
            logger.error(f"API: No script found for project {project_id}")
            return {"error": "No script found"}
        
        # Initialize Engine with selected Provider + Knowledge Base
        provider = get_provider(resolved_config)
        engine = StoryboardEngine(provider, knowledge_base=knowledge_base)
        
        # Parse and Analyze
        logger.info(f"API: Parsing script content...")
        scenes = ScriptParser.parse(script.content)
        logger.info(f"API: Script parsed into {len(scenes)} scenes. Calling engine...")
        
        if not scenes:
            raise HTTPException(
                status_code=400, 
                detail="Could not identify any scenes or sections in the uploaded document. "
                       "Please ensure the file contains readable text content."
            )

        # ── Persist scenes to DB (foundation for re-generation + versioning) ─
        db.query(Scene).filter(Scene.project_id == project_id).delete()
        for idx, scene in enumerate(scenes):
            db_scene = Scene(
                id=str(uuid.uuid4()),
                project_id=project_id,
                script_id=script.id,
                scene_number=idx + 1,
                heading=scene.get("heading", f"Scene {idx + 1}"),
                content=scene.get("text", ""),
                characters=json.dumps(scene.get("characters", [])),
            )
            db.add(db_scene)
        db.commit()
        logger.info(f"API: {len(scenes)} scenes persisted to DB")

        storyboard_style = resolved_config.storyboard_style or "oscar_prestige"
        frames: list = await engine.analyze_script(scenes, storyboard_style=storyboard_style)
        
        # Clear old frames for this project if any
        db.query(StoryboardFrame).filter(StoryboardFrame.project_id == project_id).delete()
        
        # Save to DB
        logger.info(f"API: Saving {len(frames)} analyzed frames to database...")
        for frame in frames:
            scene_chars = json.dumps(
                next((s.get("characters", []) for s in scenes if scenes.index(s) + 1 == frame['scene_number']), [])
            )
            db_frame = StoryboardFrame(
                id=str(uuid.uuid4()),
                project_id=project_id,
                scene_number=frame['scene_number'],
                heading=frame.get('heading', ''),
                description=frame['description'],
                intensity_score=frame['intensity_score'],
                intensity_type=frame['intensity_type'],
                moment_summary=frame.get('moment_summary', ''),
                shot_type=frame.get('shot_type', ''),
                camera_movement=frame.get('camera_movement', ''),
                lens=frame.get('lens', ''),
                lighting=frame.get('lighting', ''),
                image_path=frame.get('image_path'),
                motion_preset=frame.get('motion_preset', 'dolly_in'),
                scene_characters=scene_chars,
            )
            db.add(db_frame)
        
        db.commit()
        logger.info(f"API: Generation and DB persistence complete for project {project_id}")
        GovernanceEngine.audit_generation(project_id, len(frames), storyboard_style)

        # ── Character Extraction ─────────────────────────────────────────────
        script_title = script.filename or "Untitled Script"
        try:
            char_profiles = await engine.extract_characters(scenes, genre="drama", script_title=script_title)
            db.query(Character).filter(Character.project_id == project_id).delete()
            for cp in char_profiles:
                db_char = Character(
                    id=str(uuid.uuid4()),
                    project_id=project_id,
                    name=cp["name"],
                    description=cp.get("description", ""),
                    age_range=cp.get("age_range", ""),
                    role=cp.get("role", "supporting"),
                    wardrobe=cp.get("wardrobe", ""),
                    visual_prompt=cp.get("visual_prompt", ""),
                    voice_id=cp.get("voice_id", "alloy"),
                    voice_description=cp.get("voice_description", ""),
                    first_scene=cp.get("first_scene", 1),
                    scene_count=cp.get("scene_count", 0),
                    line_count=cp.get("line_count", 0),
                    is_lead=cp.get("is_lead", False),
                )
                db.add(db_char)
            db.commit()
            logger.info(f"API: {len(char_profiles)} character profiles saved for project {project_id}")
        except Exception as char_err:
            logger.warning(f"API: Character extraction skipped: {char_err}")

        # ── Knowledge Base: distill insights ─────────────────────────────────
        try:
            learned = await knowledge_base.distill_insights_from_analysis(
                provider=provider,
                scenes=scenes,
                frames=frames,
                genre="drama",
                script_title=script_title,
            )
            logger.info(f"KB: Distilled {learned} new insights from '{script_title}'")
        except Exception as kb_err:
            logger.warning(f"KB: Insight distillation skipped: {kb_err}")

        # Return the frames from DB
        db_frames = db.query(StoryboardFrame).filter(StoryboardFrame.project_id == project_id).all()
        return db_frames
        
    except Exception as e:
        logger.error(f"API: Generation failed for project {project_id}: {e}")
        error_msg = str(e)
        status_code = 500
        if "Insufficient Credits" in error_msg:
            status_code = 402
        return JSONResponse(status_code=status_code, content={"error": error_msg, "type": "provider_error"})
    finally:
        db.close()

@app.post("/projects/{project_id}/generate-stream")
async def generate_storyboard_stream(project_id: str, config: ProviderConfig):
    """
    SSE streaming endpoint for storyboard generation.
    Emits one JSON event per scene as it completes, allowing the frontend
    to populate frames progressively rather than waiting for full completion.

    Event types:
      {type: "start",    total: N}
      {type: "frame",    frame: {...}, progress: {current: N, total: N}}
      {type: "complete", total: N}
      {type: "error",    message: "..."}
    """
    from fastapi.responses import StreamingResponse as _SR
    import json as _json

    async def event_stream():
        db = SessionLocal()
        try:
            resolved_config = _merge_with_persisted_config(config)
            script = db.query(Script).filter(Script.project_id == project_id).order_by(Script.version.desc()).first()
            if not script:
                yield f"data: {_json.dumps({'type': 'error', 'message': 'No script found for this project'})}\n\n"
                return

            provider = get_provider(resolved_config)
            engine = StoryboardEngine(provider, knowledge_base=knowledge_base)
            scenes = ScriptParser.parse(script.content, format_hint=script.script_format or "auto")

            if not scenes:
                yield f"data: {_json.dumps({'type': 'error', 'message': 'Could not identify any scenes in this document'})}\n\n"
                return

            # Detect genre
            script_sample = "\n".join([s.get("heading", "") for s in scenes[:5]])
            import re as _re
            raw_genre = await provider.generate_text(
                f"Identify the primary film genre in one word (Action, Drama, Horror, Comedy, Thriller, SciFi, Western, Noir, Fantasy, Romance, War, etc.):\n\n{script_sample}"
            )
            genre = _re.sub(r'[^a-zA-Z\-]', '', raw_genre.strip().split()[0]).lower()

            from genre_vault import get_style_guidance as _gsg  # type: ignore
            from style_vault import get_style as _gs  # type: ignore
            style_guidance = _gsg(genre)
            storyboard_style = resolved_config.storyboard_style or "oscar_prestige"
            visual_style = _gs(storyboard_style)
            wisdom_context = engine.knowledge_base.get_wisdom_context(genre) if engine.knowledge_base else ""

            # Clear old frames
            db.query(StoryboardFrame).filter(StoryboardFrame.project_id == project_id).delete()
            db.commit()

            total = len(scenes)
            yield f"data: {_json.dumps({'type': 'start', 'total': total, 'genre': genre, 'style': storyboard_style})}\n\n"
            logger.info(f"SSE: Starting stream for project {project_id} | {total} scenes | genre={genre}")

            for i, scene in enumerate(scenes):
                frame = await engine.analyze_single_scene(
                    scene=scene, scene_index=i, total_scenes=total,
                    genre=genre, style_guidance=style_guidance,
                    visual_style=visual_style, wisdom_context=wisdom_context,
                )
                # Persist to DB
                db_frame = StoryboardFrame(
                    id=str(uuid.uuid4()), project_id=project_id,
                    scene_number=frame['scene_number'], heading=frame.get('heading', ''),
                    description=frame['description'], intensity_score=frame['intensity_score'],
                    intensity_type=frame['intensity_type'], moment_summary=frame.get('moment_summary', ''),
                    shot_type=frame.get('shot_type', ''), camera_movement=frame.get('camera_movement', ''),
                    lens=frame.get('lens', ''), lighting=frame.get('lighting', ''),
                    image_path=frame.get('image_path'),
                    motion_preset=frame.get('motion_preset', 'dolly_in'),
                )
                db.add(db_frame)
                db.commit()
                db.refresh(db_frame)

                frame['id'] = db_frame.id
                event = {'type': 'frame', 'frame': frame, 'progress': {'current': i + 1, 'total': total}}
                yield f"data: {_json.dumps(event)}\n\n"
                logger.info(f"SSE: Streamed scene {i+1}/{total} to client (image={'✓' if frame.get('image_path') else '✗'})")

            GovernanceEngine.audit_generation(project_id, total, storyboard_style)
            yield f"data: {_json.dumps({'type': 'complete', 'total': total})}\n\n"
            logger.info(f"SSE: Stream complete for project {project_id}")

        except Exception as e:
            logger.error(f"SSE: Stream error for project {project_id}: {e}", exc_info=True)
            yield f"data: {_json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        finally:
            db.close()

    return _SR(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )

@app.post("/frames/{frame_id}/generate-image")
async def generate_frame_image(frame_id: str):
    db = SessionLocal()
    try:
        frame = db.query(StoryboardFrame).filter(StoryboardFrame.id == frame_id).first()
        if not frame:
            raise HTTPException(status_code=404, detail="Frame not found")
        
        saved_config = _get_persisted_provider_config(db)
        if saved_config:
            provider = get_provider(saved_config)
            saved_style = saved_config.storyboard_style or "oscar_prestige"
        else:
            provider = get_provider(ProviderConfig(type="local", api_key=""))
            saved_style = "oscar_prestige"

        engine = StoryboardEngine(provider)

        # ── Character Visual Consistency Injection ──
        chars = db.query(Character).filter(Character.project_id == frame.project_id).all()
        scene_char_names = set(json.loads(frame.scene_characters or "[]"))
        relevant_char_profiles = []
        for c in chars:
            if (scene_char_names and c.name in scene_char_names) or c.is_lead:
                relevant_char_profiles.append({
                    "name": c.name,
                    "visual_prompt": c.visual_prompt or f"{c.name}, {c.description or ''}, signature wardrobe: {c.wardrobe or ''}",
                    "description": c.description,
                    "wardrobe": c.wardrobe,
                })

        logger.info(
            f"IMAGE GEN: Generating frame {frame.scene_number} with {len(relevant_char_profiles)} character consistency profiles"
        )

        result = await engine.generate_visual(
            frame_description=frame.description,
            genre="drama",
            storyboard_style=saved_style,
            character_profiles=relevant_char_profiles,
        )
        
        image_url = result.get("image_url", "")
        frame.image_path = image_url
        db.commit()
        
        return {
            "status": "success",
            "image_url": image_url,
            "model_used": result.get("model_used", "unknown"),
            "provider": result.get("provider", "unknown"),
            "attempts": result.get("attempts", []),
            "characters_injected": [c["name"] for c in relevant_char_profiles]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"IMAGE GEN: Error generating frame {frame_id}: {e}")
        # Fallback to free reliable visual
        engine = StoryboardEngine(get_provider(ProviderConfig(type="local", api_key="")))
        image_url = engine._get_pollinations_url(frame.description or "Cinematic scene", seed=random.randint(100, 9999))
        frame.image_path = image_url
        db.commit()
        return {
            "status": "success",
            "image_url": image_url,
            "model_used": "Pollinations.ai (Fallback)",
            "provider": "Free Fallback",
            "attempts": [{"model": "Pollinations.ai", "status": "success"}]
        }
    finally:
        db.close()

@app.post("/frames/{frame_id}/generate-animatic")
async def generate_frame_animatic(frame_id: str, body: Optional[dict] = None):
    """
    Generate a 16:9 cinematic motion animatic video (.mp4) for a storyboard frame.
    Body: {"motion_preset": "dolly_in", "duration": 3.5}
    """
    db = SessionLocal()
    try:
        frame = db.query(StoryboardFrame).filter(StoryboardFrame.id == frame_id).first()
        if not frame:
            raise HTTPException(status_code=404, detail="Frame not found")

        motion_preset = (body or {}).get("motion_preset") or frame.motion_preset or "dolly_in"
        duration = float((body or {}).get("duration") or frame.video_duration or 3.5)

        filename = f"animatic_{frame.id}_{motion_preset}.mp4"
        output_path = VideoEngine.generate_frame_animatic(
            image_source=frame.image_path,
            motion_preset=motion_preset,
            duration=duration,
            output_filename=filename,
        )

        video_url = f"/static/videos/{filename}"
        frame.video_path = video_url
        frame.motion_preset = motion_preset
        frame.video_duration = duration
        frame.video_status = "ready"
        db.commit()

        logger.info(f"ANIMATIC: Frame {frame.scene_number} generated -> {video_url}")
        return {
            "status": "success",
            "frame_id": frame_id,
            "video_url": video_url,
            "motion_preset": motion_preset,
            "duration": duration,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ANIMATIC: Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/projects/{project_id}/generate-all-images")
async def generate_all_project_images(project_id: str, body: Optional[dict] = None):
    """
    Batch auto-generates visual images for all frames in a project.
    Body: {"force": true/false}
    """
    db = SessionLocal()
    try:
        frames = db.query(StoryboardFrame).filter(StoryboardFrame.project_id == project_id).order_by(StoryboardFrame.scene_number.asc()).all()
        if not frames:
            raise HTTPException(status_code=404, detail="No storyboard frames found for this project.")
        
        saved_config = _get_persisted_provider_config(db)
        provider = get_provider(saved_config) if saved_config else get_provider(ProviderConfig(type="local", api_key=""))
        engine = StoryboardEngine(provider, knowledge_base=knowledge_base)
        saved_style = saved_config.storyboard_style if saved_config else "oscar_prestige"

        chars = db.query(Character).filter(Character.project_id == project_id).all()
        char_profiles = [
            {"name": c.name, "visual_prompt": c.visual_prompt or f"{c.name}, {c.description or ''}"}
            for c in chars
        ]

        force = (body or {}).get("force", False)
        rendered_count = 0

        for frame in frames:
            if frame.image_path and not force:
                continue

            scene_chars = []
            try:
                scene_char_names = set(json.loads(frame.scene_characters or "[]"))
                scene_chars = [cp for cp in char_profiles if cp["name"] in scene_char_names]
            except Exception:
                scene_chars = char_profiles[:2]

            try:
                res = await engine.generate_visual(
                    frame_description=frame.description,
                    genre="drama",
                    storyboard_style=saved_style,
                    character_profiles=scene_chars,
                )
                frame.image_path = res.get("image_url")
            except Exception:
                frame.image_path = engine._get_pollinations_url(frame.description, seed=frame.scene_number * 33)

            rendered_count += 1

        db.commit()
        logger.info(f"BATCH IMAGES: Rendered {rendered_count} frames for project {project_id}")

        return {
            "status": "success",
            "rendered_count": rendered_count,
            "total_frames": len(frames),
            "frames": [
                {
                    "id": f.id,
                    "scene_number": f.scene_number,
                    "heading": f.heading,
                    "description": f.description,
                    "intensity_score": f.intensity_score,
                    "intensity_type": f.intensity_type,
                    "moment_summary": f.moment_summary,
                    "shot_type": f.shot_type,
                    "camera_movement": f.camera_movement,
                    "lens": f.lens,
                    "lighting": f.lighting,
                    "image_path": f.image_path,
                    "video_path": f.video_path,
                    "motion_preset": f.motion_preset,
                }
                for f in frames
            ]
        }
    finally:
        db.close()

@app.post("/projects/{project_id}/generate-all-animatics")
async def generate_all_project_animatics(project_id: str, body: Optional[dict] = None):
    """
    Batch auto-generates 16:9 cinematic motion animatic video clips for all frames in a project,
    and compiles the master animatic reel (.mp4).
    """
    db = SessionLocal()
    try:
        frames = db.query(StoryboardFrame).filter(StoryboardFrame.project_id == project_id).order_by(StoryboardFrame.scene_number.asc()).all()
        if not frames:
            raise HTTPException(status_code=404, detail="No storyboard frames found for this project.")

        rendered_videos = []
        for frame in frames:
            motion = frame.motion_preset or "dolly_in"
            duration = float(frame.video_duration or 3.5)
            filename = f"animatic_{frame.id}_{motion}.mp4"
            try:
                VideoEngine.generate_frame_animatic(
                    image_source=frame.image_path,
                    motion_preset=motion,
                    duration=duration,
                    output_filename=filename,
                )
                video_url = f"/static/videos/{filename}"
                frame.video_path = video_url
                frame.video_status = "ready"
                rendered_videos.append(video_url)
            except Exception as e:
                logger.error(f"ANIMATIC: Failed for frame {frame.scene_number}: {e}")

        db.commit()

        # Compile master reel
        master_reel_url = None
        try:
            frame_dicts = [
                {
                    "id": f.id,
                    "scene_number": f.scene_number,
                    "heading": f.heading,
                    "shot_type": f.shot_type,
                    "description": f.description,
                    "image_path": f.image_path,
                    "motion_preset": f.motion_preset or "dolly_in",
                    "video_duration": f.video_duration or 3.5,
                }
                for f in frames
            ]
            reel_file = f"master_reel_{project_id}.mp4"
            VideoEngine.compile_master_reel(frame_dicts, output_filename=reel_file)
            master_reel_url = f"/static/videos/{reel_file}"
        except Exception as reel_err:
            logger.error(f"ANIMATIC: Master reel compilation failed: {reel_err}")

        return {
            "status": "success",
            "animated_count": len(rendered_videos),
            "total_frames": len(frames),
            "master_reel_url": master_reel_url,
        }
    finally:
        db.close()

@app.get("/projects/{project_id}")
async def get_project(project_id: str):
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {"error": "Project not found"}
        # Return serialized nested data
        db_frames = db.query(StoryboardFrame).filter(StoryboardFrame.project_id == project_id).order_by(StoryboardFrame.scene_number.asc()).all()
        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "frames": [
                {
                    "id": f.id,
                    "scene_number": f.scene_number,
                    "heading": f.heading,
                    "description": f.description,
                    "intensity_score": f.intensity_score,
                    "intensity_type": f.intensity_type,
                    "moment_summary": f.moment_summary,
                    "shot_type": f.shot_type,
                    "camera_movement": f.camera_movement,
                    "lens": f.lens,
                    "lighting": f.lighting,
                    "image_path": f.image_path,
                    "video_path": f.video_path,
                    "motion_preset": f.motion_preset,
                    "video_duration": f.video_duration,
                    "video_status": f.video_status,
                }
                for f in db_frames
            ]
        }
    finally:
        db.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
