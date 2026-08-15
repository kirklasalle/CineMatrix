"""
Storyboard AI — Example Scripts Service & Catalog.
Provides structured discovery, previews, and 1-click project initialization
for the 27 world-class sample scripts in docs/examples/.
"""
import os
import io
import json
import uuid
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("storyboard-api")

EXAMPLES_BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "docs", "examples")
)

EXAMPLES_CATALOG: List[Dict[str, Any]] = [
    # ── 1. Ingestion Formats (9 files) ───────────────────────────────────────
    {
        "id": "format-hollywood-fountain",
        "category": "formats",
        "filename": "01_screenplay_hollywood.fountain",
        "title": "The Golden Heist",
        "format": "fountain",
        "genre": "Heist Action",
        "style": "oscar_prestige",
        "target_engine": "Screenplay Parser",
        "duration": "3 min",
        "scene_count": 3,
        "description": "Full Hollywood Fountain screenplay standard with dual dialogue, transitions, parentheticals, and title metadata.",
        "tags": ["fountain", "dual-dialogue", "action", "heist"],
    },
    {
        "id": "format-final-draft-fdx",
        "category": "formats",
        "filename": "02_final_draft_noir.fdx",
        "title": "Shadows in the Rain",
        "format": "fdx",
        "genre": "Film Noir",
        "style": "film_noir",
        "target_engine": "Final Draft XML Parser",
        "duration": "2 min",
        "scene_count": 2,
        "description": "Native Final Draft 12 XML screenplay with scene properties, character voiceover, and Venetian blind lighting.",
        "tags": ["fdx", "final-draft", "xml", "noir"],
    },
    {
        "id": "format-television-docx",
        "category": "formats",
        "filename": "03_television_drama.docx",
        "title": "Redacted Protocol",
        "format": "docx",
        "genre": "Political Thriller",
        "style": "neo_noir_neon",
        "target_engine": "Word Document Parser",
        "duration": "3 min",
        "scene_count": 2,
        "description": "Microsoft Word .docx 1-hour episodic TV Pilot script with act headers and centered character cues.",
        "tags": ["docx", "word", "television", "pilot"],
    },
    {
        "id": "format-feature-pdf",
        "category": "formats",
        "filename": "04_feature_thriller.pdf",
        "title": "Deep Submersion",
        "format": "pdf",
        "genre": "Submarine Thriller",
        "style": "oscar_prestige",
        "target_engine": "PDF Screenplay Extractor",
        "duration": "2 min",
        "scene_count": 1,
        "description": "Industry-standard Courier 12pt PDF screenplay testing automated text coordinate extraction and scene detection.",
        "tags": ["pdf", "screenplay", "submarine", "thriller"],
    },
    {
        "id": "format-av-commercial-doc",
        "category": "formats",
        "filename": "05_av_commercial_doc.txt",
        "title": "Echoes of the Deep",
        "format": "txt",
        "genre": "Documentary",
        "style": "dogme_naturalist",
        "target_engine": "AV Two-Column Parser",
        "duration": "60 sec",
        "scene_count": 4,
        "description": "Two-column Audio/Visual script layout for documentary, commercial, and broadcast television storyboarding.",
        "tags": ["av-script", "commercial", "documentary", "two-column"],
    },
    {
        "id": "format-stage-play-broadway",
        "category": "formats",
        "filename": "06_stage_play_broadway.txt",
        "title": "The Winter Solstice",
        "format": "txt",
        "genre": "Victorian Drama",
        "style": "painted_realism",
        "target_engine": "Stage Play Parser",
        "duration": "4 min",
        "scene_count": 2,
        "description": "Broadway theatrical stage play script with ACT/SCENE numbering, centered characters, and bracketed stage directions.",
        "tags": ["stage-play", "theatre", "broadway", "drama"],
    },
    {
        "id": "format-comic-book-cbz",
        "category": "formats",
        "filename": "07_comic_book_issue.cbz",
        "title": "CyberValkyrie: Neon Dawn",
        "format": "cbz",
        "genre": "Cyberpunk Action",
        "style": "comic_book",
        "target_engine": "Comic Book CBZ Parser",
        "duration": "2 pages",
        "scene_count": 2,
        "description": "Standard Comic Book Archive (.cbz) with ComicInfo.xml metadata and sequential panel breakdown scripts.",
        "tags": ["cbz", "comic-book", "graphic-novel", "cyberpunk"],
    },
    {
        "id": "format-novel-chapter-epub",
        "category": "formats",
        "filename": "08_novel_chapter_prose.epub",
        "title": "Chronicles of the Starfarer",
        "format": "epub",
        "genre": "Sci-Fi Space Opera",
        "style": "concept_art_digital",
        "target_engine": "ePub Digital Book Parser",
        "duration": "Chapter 1",
        "scene_count": 1,
        "description": "Electronic Publication (.epub) novel chapter demonstrating prose fiction chunking into visual storyboard scenes.",
        "tags": ["epub", "novel", "prose", "sci-fi"],
    },
    {
        "id": "format-standard-screenplay-txt",
        "category": "formats",
        "filename": "09_standard_screenplay.txt",
        "title": "Midnight Crossing",
        "format": "txt",
        "genre": "Cold War Espionage",
        "style": "film_noir",
        "target_engine": "Standard Text Parser",
        "duration": "2 min",
        "scene_count": 1,
        "description": "Plain-text industry screenplay with classic INT./EXT. headers, character slugs, and action lines.",
        "tags": ["txt", "screenplay", "espionage", "cold-war"],
    },

    # ── 2. Flagship AI Engines (6 files) ─────────────────────────────────────
    {
        "id": "engine-story-doctor-15-beats",
        "category": "engines",
        "filename": "10_story_doctor_15_beats.fountain",
        "title": "The Alchemist's Horizon",
        "format": "fountain",
        "genre": "Fantasy Drama",
        "style": "oscar_prestige",
        "target_engine": "Story Doctor (15 Beats)",
        "duration": "15 scenes",
        "scene_count": 15,
        "description": "The definitive Blake Snyder 15-Beat structural masterclass with all 15 beats for tension curve and coverage analysis.",
        "tags": ["story-doctor", "15-beats", "blake-snyder", "coverage"],
    },
    {
        "id": "engine-table-read-voices",
        "category": "engines",
        "filename": "11_table_read_ensemble_cast.fountain",
        "title": "The Summit at Blackwood Manor",
        "format": "fountain",
        "genre": "Mystery Thriller",
        "style": "film_noir",
        "target_engine": "Table Read Studio",
        "duration": "4 min",
        "scene_count": 1,
        "description": "6-character vocal ensemble mapped directly to Alloy, Echo, Fable, Onyx, Nova, and Shimmer voice models with teleprompter timing.",
        "tags": ["table-read", "voice-casting", "ensemble", "tts"],
    },
    {
        "id": "engine-action-animatic-motion",
        "category": "engines",
        "filename": "12_action_animatic_motion.fountain",
        "title": "Velocity Protocol: Rooftop Pursuit",
        "format": "fountain",
        "genre": "Action Thriller",
        "style": "concept_art_digital",
        "target_engine": "Camera Motion Video Engine",
        "duration": "3 min",
        "scene_count": 1,
        "description": "High-octane rooftop chase tagged with director cues for all 6 motion presets (Dolly In, Out, Pan Left, Right, Handheld, Slow-Mo).",
        "tags": ["video-animatics", "camera-motion", "ken-burns", "action"],
    },
    {
        "id": "engine-graphic-novel-manga",
        "category": "engines",
        "filename": "13_graphic_novel_manga_studio.fountain",
        "title": "Ronin-09: Electric Bushido",
        "format": "fountain",
        "genre": "Cyberpunk Samurai",
        "style": "manga_kinetic",
        "target_engine": "Graphic Novel Studio",
        "duration": "4 panels",
        "scene_count": 1,
        "description": "Multi-panel sequential scenes optimized for 4-Quadrant, 6-Grid, and Manga Split layouts with sound effect bursts.",
        "tags": ["graphic-novel", "manga", "panel-layout", "comic-print"],
    },
    {
        "id": "engine-audio-score-foley",
        "category": "engines",
        "filename": "14_cinematic_audio_score_foley.fountain",
        "title": "Abyssal Breach",
        "format": "fountain",
        "genre": "Sci-Fi Horror",
        "style": "expressionist_horror",
        "target_engine": "Audio Scoring & Foley",
        "duration": "2 min",
        "scene_count": 1,
        "description": "Procedural soundtrack synthesis (Cinematic Epic / Horror Ambient) and physical foley sound effects triggers.",
        "tags": ["audio-scoring", "soundtrack", "foley", "sfx"],
    },
    {
        "id": "engine-character-archetypes-lookbook",
        "category": "engines",
        "filename": "15_character_archetypes_lookbook.fountain",
        "title": "The Sovereign's Gambit",
        "format": "fountain",
        "genre": "Epic Fantasy",
        "style": "golden_age_hollywood",
        "target_engine": "Character Look-Book",
        "duration": "Coronation Scene",
        "scene_count": 1,
        "description": "8 distinct Jungian archetypes (Hero, Sage, Rebel, Shadow, Mentor, Trickster, Caregiver, Sovereign) for look-book generation.",
        "tags": ["character-library", "jungian-archetypes", "look-book", "casting"],
    },

    # ── 3. Genres & Visual Art Styles (9 files) ──────────────────────────────
    {
        "id": "genre-cyberpunk-neo-noir",
        "category": "genres",
        "filename": "16_sci_fi_cyberpunk_neo_noir.fountain",
        "title": "Nexus Zero: Synthetic Tears",
        "format": "fountain",
        "genre": "Sci-Fi / Cyberpunk",
        "style": "neo_noir_neon",
        "target_engine": "Style Vault",
        "duration": "2 min",
        "scene_count": 1,
        "description": "Blade Runner-inspired wet streets, volumetric neon cyan/amber split, and dark futuristic anamorphic flares.",
        "tags": ["cyberpunk", "neo-noir", "blade-runner", "neon"],
    },
    {
        "id": "genre-historical-prestige-drama",
        "category": "genres",
        "filename": "17_historical_prestige_drama.fountain",
        "title": "Crown of Iron: The Treaty of 1588",
        "format": "fountain",
        "genre": "Historical Drama",
        "style": "oscar_prestige",
        "target_engine": "Prestige Cinema",
        "duration": "3 min",
        "scene_count": 1,
        "description": "Roger Deakins natural candlelight, Rembrandt chiaroscuro, and royal court intrigue.",
        "tags": ["historical", "drama", "oscar-prestige", "candelabra"],
    },
    {
        "id": "genre-horror-psychological-dread",
        "category": "genres",
        "filename": "18_horror_psychological_dread.fountain",
        "title": "The Whispering Asylum",
        "format": "fountain",
        "genre": "Psychological Horror",
        "style": "expressionist_horror",
        "target_engine": "Horror Cinematography",
        "duration": "2 min",
        "scene_count": 1,
        "description": "Caligari distorted geometry, elongated shadows, Nosferatu angles, and claustrophobic asylum terror.",
        "tags": ["horror", "expressionist", "dread", "nosferatu"],
    },
    {
        "id": "genre-action-blockbuster-kinetic",
        "category": "genres",
        "filename": "19_action_blockbuster_kinetic.fountain",
        "title": "Apex Overdrive",
        "format": "fountain",
        "genre": "Action Blockbuster",
        "style": "comic_book",
        "target_engine": "Dynamic Action",
        "duration": "2 min",
        "scene_count": 1,
        "description": "High-velocity highway heist with Jack Kirby energy, bold comic outlines, and explosion choreography.",
        "tags": ["action", "comic-book", "heist", "blockbuster"],
    },
    {
        "id": "genre-whimsical-comedy-symmetry",
        "category": "genres",
        "filename": "20_whimsical_comedy_symmetry.fountain",
        "title": "The Eccentric Taxonomy of Professor Pym",
        "format": "fountain",
        "genre": "Whimsical Comedy",
        "style": "wes_anderson",
        "target_engine": "Symmetrical Staging",
        "duration": "3 min",
        "scene_count": 1,
        "description": "Wes Anderson bilateral symmetry, pastel mustard/mint palette, and deadpan cryptozoological humor.",
        "tags": ["wes-anderson", "comedy", "symmetry", "pastel"],
    },
    {
        "id": "genre-romantic-impressionist-memory",
        "category": "genres",
        "filename": "21_romantic_impressionist_memory.fountain",
        "title": "Midnight in Kowloon: Days of Rain",
        "format": "fountain",
        "genre": "Romance Drama",
        "style": "wong_kar_wai",
        "target_engine": "Impressionist Mood",
        "duration": "3 min",
        "scene_count": 1,
        "description": "Wong Kar-wai / Christopher Doyle step-printed motion blur, isolated neon pools, and poetic longing.",
        "tags": ["romance", "wong-kar-wai", "impressionist", "motion-blur"],
    },
    {
        "id": "genre-gritty-documentary-verite",
        "category": "genres",
        "filename": "22_gritty_documentary_verite.txt",
        "title": "Undercover Steel: Voices from the Line",
        "format": "txt",
        "genre": "Cinema Verité",
        "style": "dogme_naturalist",
        "target_engine": "Naturalist Documentary",
        "duration": "3 min",
        "scene_count": 1,
        "description": "Available industrial light, handheld camera shake, raw unvarnished truth from the blast furnace floor.",
        "tags": ["documentary", "cinema-verite", "dogme", "naturalist"],
    },
    {
        "id": "genre-animation-fantasy-fairytale",
        "category": "genres",
        "filename": "23_animation_fantasy_fairytale.fountain",
        "title": "The Clockwork Dryad",
        "format": "fountain",
        "genre": "Anime / Fantasy",
        "style": "anime_cinematic",
        "target_engine": "Animation Staging",
        "duration": "3 min",
        "scene_count": 1,
        "description": "Studio Ghibli painterly moss warmth, atmospheric sunbeams, and enchanting clockwork heart awakening.",
        "tags": ["anime", "ghibli", "fantasy", "animation"],
    },
    {
        "id": "genre-spaghetti-western-standoff",
        "category": "genres",
        "filename": "24_spaghetti_western_standoff.fountain",
        "title": "Dust, Blood, and Gold: The Three Coffins",
        "format": "fountain",
        "genre": "Spaghetti Western",
        "style": "classic_pencil",
        "target_engine": "Extreme Cinematography",
        "duration": "3 min",
        "scene_count": 1,
        "description": "Sergio Leone 3-way circular graveyard standoff with rapid extreme close-ups, dust, and high noon tension.",
        "tags": ["western", "sergio-leone", "standoff", "pencil-sketch"],
    },

    # ── 4. Duration Spectrum Tiers (3 files) ─────────────────────────────────
    {
        "id": "spectrum-micro-1min",
        "category": "spectrum",
        "filename": "25_micro_scene_1min.fountain",
        "title": "The Cold Call",
        "format": "fountain",
        "genre": "Micro Thriller",
        "style": "oscar_prestige",
        "target_engine": "Rapid 10-Second Test",
        "duration": "1 Minute",
        "scene_count": 1,
        "description": "1-minute micro pitch scene (1 scene, 3 shots) for instant 10-second end-to-end testing and rapid iteration.",
        "tags": ["micro-scene", "1-min", "fast-test", "benchmark"],
    },
    {
        "id": "spectrum-short-film-5min",
        "category": "spectrum",
        "filename": "26_short_film_5min.fountain",
        "title": "Last Flight of the Osprey",
        "format": "fountain",
        "genre": "Aviation Drama",
        "style": "oscar_prestige",
        "target_engine": "Standard Benchmark",
        "duration": "5 Minutes",
        "scene_count": 5,
        "description": "5-minute short film across 5 scenes with a complete 3-act arc for evaluating pacing and presentation decks.",
        "tags": ["short-film", "5-min", "standard-benchmark", "3-act"],
    },
    {
        "id": "spectrum-tv-pilot-10min",
        "category": "spectrum",
        "filename": "27_tv_pilot_teaser_10min.fountain",
        "title": "Cipher: Season 1 - Genesis",
        "format": "fountain",
        "genre": "Sci-Fi Thriller",
        "style": "oscar_prestige",
        "target_engine": "Production Pilot Benchmark",
        "duration": "10 Minutes",
        "scene_count": 10,
        "description": "10-minute TV pilot teaser & Act I across 10 scenes, multi-plot ensemble, and comprehensive multi-scene exports.",
        "tags": ["tv-pilot", "10-min", "teaser", "ensemble-pilot"],
    },
]


def list_examples(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return all catalog examples or filtered by category."""
    if category and category != "all":
        return [ex for ex in EXAMPLES_CATALOG if ex["category"] == category]
    return EXAMPLES_CATALOG


def get_example_by_id(example_id: str) -> Optional[Dict[str, Any]]:
    """Lookup an example by ID or filename."""
    for ex in EXAMPLES_CATALOG:
        if ex["id"] == example_id or ex["filename"] == example_id:
            return ex
    return None


def read_example_content(category: str, filename: str) -> Dict[str, Any]:
    """
    Read content of an example script file.
    Returns metadata and raw text / preview string.
    """
    file_path = os.path.join(EXAMPLES_BASE_DIR, category, filename)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Example file not found: {category}/{filename}")

    ext = filename.rsplit(".", 1)[-1].lower()
    
    # Read binary or text
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    text_preview = ""
    is_binary = ext in ("docx", "pdf", "cbz", "epub")

    if ext == "docx":
        from parsers.docx_parser import extract_docx_text
        text_preview = extract_docx_text(file_bytes)
    elif ext == "pdf":
        try:
            import fitz
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text_preview = "\n".join([page.get_text() or "" for page in doc])
        except Exception:
            text_preview = "[PDF Screenplay Document — Binary]"
    elif ext == "cbz":
        from parsers.comic_parser import parse_cbz
        res = parse_cbz(file_bytes)
        text_preview = "\n\n".join([f"{s['heading']}\n{s['content']}" for s in res.get("scenes", [])])
    elif ext == "epub":
        from parsers.epub_parser import parse_epub
        res = parse_epub(file_bytes)
        text_preview = "\n\n".join([f"{s['heading']}\n{s['content']}" for s in res.get("scenes", [])])
    else:
        try:
            text_preview = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text_preview = file_bytes.decode("latin-1", errors="replace")

    return {
        "filename": filename,
        "category": category,
        "format": ext,
        "is_binary": is_binary,
        "content": text_preview,
        "byte_size": len(file_bytes),
    }
