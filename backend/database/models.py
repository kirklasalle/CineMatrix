"""
Storyboard AI — Database Models (Canonical).
All SQLAlchemy ORM models. Single source of truth.
"""
from sqlalchemy import create_engine, Column, String, Integer, Float, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship
from time_utils import utc_now  # type: ignore
import os


class Base(DeclarativeBase):
    pass


# ── Core Project Models ───────────────────────────────────────────────────────

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=utc_now)

    scripts = relationship("Script", back_populates="project")
    frames = relationship("StoryboardFrame", back_populates="project")
    scenes = relationship("Scene", back_populates="project")
    characters = relationship("Character", back_populates="project")


class Script(Base):
    __tablename__ = "scripts"
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"))
    content = Column(Text, nullable=False)
    filename = Column(String)
    script_format = Column(String, default="text")   # fdx, fountain, docx, pdf, text
    version = Column(Integer, default=1)

    project = relationship("Project", back_populates="scripts")
    scenes = relationship("Scene", back_populates="script")


class Scene(Base):
    """Persisted scene — foundation for re-generation and version history."""
    __tablename__ = "scenes"
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"))
    script_id = Column(String, ForeignKey("scripts.id"))
    scene_number = Column(Integer)
    heading = Column(String)
    content = Column(Text)
    characters = Column(Text, default="[]")   # JSON list of character names

    project = relationship("Project", back_populates="scenes")
    script = relationship("Script", back_populates="scenes")


class StoryboardFrame(Base):
    __tablename__ = "storyboard_frames"
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"))
    scene_number = Column(Integer)
    heading = Column(String)
    description = Column(Text)
    image_path = Column(String)
    intensity_score = Column(Float)
    intensity_type = Column(String)      # "Action Peak", "Emotional Peak", "Lull"
    moment_summary = Column(Text)
    shot_type = Column(String)           # ECU, CU, MCU, MS, WS, EWS, OTS, POV …
    camera_movement = Column(String)     # Static, Dolly, Pan, Handheld, Crane …
    lens = Column(String)                # 24mm, 50mm anamorphic, telephoto …
    lighting = Column(String)            # Chiaroscuro, natural, three-point …
    scene_characters = Column(Text, default="[]")  # JSON list of character names in frame
    
    # Multimodal Video / Animatic Attributes (Phase 4)
    video_path = Column(String, nullable=True)          # Local MP4 path or cloud video URL
    video_duration = Column(Float, default=4.0)         # Duration in seconds
    motion_preset = Column(String, default="dolly_in")  # dolly_in, dolly_out, pan_left, pan_right, handheld, slow_motion
    video_status = Column(String, default="none")       # none, generating, ready, failed

    project = relationship("Project", back_populates="frames")


# ── Character Models ──────────────────────────────────────────────────────────

class Character(Base):
    """
    Per-project character with full visual profile and voice assignment.
    Enables:
      1. Consistent visual appearance across all storyboard frames
      2. Voice assignment for TTS read-throughs
      3. Character arc tracking across scenes
    """
    __tablename__ = "characters"
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"))
    name = Column(String, nullable=False)

    # Visual profile — drives image generation consistency
    description = Column(Text)          # Full physical appearance
    age_range = Column(String)          # "30s", "teenage", "elderly"
    role = Column(String)               # narrative role
    wardrobe = Column(Text)             # Signature clothing and style
    visual_prompt = Column(Text)        # Compiled image-gen prompt fragment

    # Voice / Read-Through
    voice_id = Column(String)           # alloy, echo, fable, onyx, nova, shimmer
    voice_provider = Column(String, default="openai")
    voice_description = Column(String)  # "Deep gravelly baritone"
    voice_notes = Column(Text)          # Director's performance notes

    # Script metadata
    first_scene = Column(Integer)
    scene_count = Column(Integer, default=0)
    line_count = Column(Integer, default=0)
    is_lead = Column(Boolean, default=False)

    project = relationship("Project", back_populates="characters")


class CharacterArchetype(Base):
    """
    Global character archetype library — grows with every project analyzed.
    Provides intelligent pre-population and cross-project visual consistency.

    Scale: unlimited entries. At ~4KB/record, 50,000 archetypes ≈ 200MB.
    Taxonomy: 14 narrative roles × 12 Jungian × 6 production tiers × 14 genre types
              = ~14,112 possible distinct type combinations.
    """
    __tablename__ = "character_archetypes"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    narrative_role = Column(String)       # protagonist, antagonist, mentor, etc.
    jungian_archetype = Column(String)    # the_hero, the_sage, the_rebel, etc.
    production_tier = Column(String)      # series_regular, recurring, day_player, etc.
    genre_type = Column(String)           # noir_detective, whistleblower, scientist, etc.
    visual_prompt = Column(Text)          # Image-generation prompt fragment
    voice_id = Column(String)             # alloy, echo, fable, onyx, nova, shimmer
    voice_description = Column(Text)      # Casting director's voice notes
    visual_style_notes = Column(Text)     # Cinematography notes for this type
    wardrobe_signature = Column(Text)     # Defining wardrobe elements
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)


# ── Configuration Model ───────────────────────────────────────────────────────

class ProviderConfiguration(Base):
    __tablename__ = "provider_configs"
    id = Column(String, primary_key=True)
    type = Column(String)
    api_key = Column(String, nullable=True)       # Stored encrypted (enc: prefix)
    base_url = Column(String, nullable=True)
    model_name = Column(String, nullable=True)
    storyboard_style = Column(String, default="oscar_prestige")


# ── Knowledge Base Model ──────────────────────────────────────────────────────

class KnowledgeEntry(Base):
    """Second Brain — Cinematic Knowledge Base entry."""
    __tablename__ = "knowledge_entries"
    id = Column(String, primary_key=True)
    knowledge_type = Column(String, nullable=False)   # cinematography, narrative, etc.
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    genre = Column(String, default="all")
    tags = Column(Text, default="[]")                 # JSON array of string tags
    source = Column(String, default="Analysis")
    confidence = Column(Float, default=0.8)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)


# ── Database Setup ────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "storyboard.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


from sqlalchemy import text  # type: ignore

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Lightweight schema migrations for existing SQLite databases
    migrations = {
        "scripts": [
            ("script_format", "VARCHAR DEFAULT 'text'"),
            ("version", "INTEGER DEFAULT 1"),
        ],
        "provider_configs": [
            ("storyboard_style", "VARCHAR DEFAULT 'oscar_prestige'"),
            ("base_url", "VARCHAR"),
            ("model_name", "VARCHAR"),
            ("api_key", "VARCHAR"),
            ("type", "VARCHAR"),
        ],
        "storyboard_frames": [
            ("heading", "VARCHAR"),
            ("moment_summary", "TEXT"),
            ("shot_type", "VARCHAR"),
            ("camera_movement", "VARCHAR"),
            ("lens", "VARCHAR"),
            ("lighting", "VARCHAR"),
            ("scene_characters", "TEXT DEFAULT '[]'"),
            ("video_path", "VARCHAR"),
            ("video_duration", "FLOAT DEFAULT 4.0"),
            ("motion_preset", "VARCHAR DEFAULT 'dolly_in'"),
            ("video_status", "VARCHAR DEFAULT 'none'"),
        ],
        "scenes": [
            ("heading", "VARCHAR"),
            ("content", "TEXT"),
            ("characters", "TEXT DEFAULT '[]'"),
        ],
        "characters": [
            ("description", "TEXT"),
            ("age_range", "VARCHAR"),
            ("role", "VARCHAR"),
            ("wardrobe", "TEXT"),
            ("visual_prompt", "TEXT"),
            ("voice_id", "VARCHAR"),
            ("voice_provider", "VARCHAR DEFAULT 'openai'"),
            ("voice_description", "VARCHAR"),
            ("voice_notes", "TEXT"),
            ("first_scene", "INTEGER"),
            ("scene_count", "INTEGER DEFAULT 0"),
            ("line_count", "INTEGER DEFAULT 0"),
            ("is_lead", "BOOLEAN DEFAULT 0"),
        ],
        "character_archetypes": [
            ("narrative_role", "VARCHAR"),
            ("jungian_archetype", "VARCHAR"),
            ("production_tier", "VARCHAR"),
            ("genre_type", "VARCHAR"),
            ("visual_prompt", "TEXT"),
            ("voice_id", "VARCHAR"),
            ("voice_description", "TEXT"),
            ("visual_style_notes", "TEXT"),
            ("wardrobe_signature", "TEXT"),
            ("usage_count", "INTEGER DEFAULT 0"),
            ("created_at", "DATETIME"),
        ],
        "knowledge_entries": [
            ("genre", "VARCHAR DEFAULT 'all'"),
            ("tags", "TEXT DEFAULT '[]'"),
            ("source", "VARCHAR DEFAULT 'Analysis'"),
            ("confidence", "FLOAT DEFAULT 0.8"),
            ("usage_count", "INTEGER DEFAULT 0"),
            ("created_at", "DATETIME"),
        ],
    }

    with engine.connect() as conn:
        for table_name, columns in migrations.items():
            try:
                result = conn.execute(text(f"PRAGMA table_info({table_name})"))
                existing_cols = {row[1] for row in result.fetchall()}
                for col_name, col_ddl in columns:
                    if col_name not in existing_cols:
                        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_ddl}"))
                        conn.commit()
            except Exception:
                pass
