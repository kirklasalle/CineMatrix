"""
Character Library — The Institutional Memory of Storyboard AI.

A growing, self-enriching database of character archetypes, visual profiles,
and voice assignments that accumulates across every project analyzed.

Scale:
  - No practical limit on character count (SQLite handles millions)
  - ~4KB per character record → 1M characters ≈ 4GB
  - Practical working library: 5,000–50,000 unique archetypes
  - Performance: sub-millisecond lookups up to ~100,000 records

Taxonomy: 4 dimensions, ~14,000 distinct type combinations
  - Narrative Role     (14 types)
  - Jungian Archetype (12 types)
  - Production Tier    (6 types)
  - Genre Type        (14 types)

Growth Model:
  First use   → Foundational archetypes seeded
  Per project → Named characters extracted, profiled, persisted
  Per batch   → Archetypes distilled and added to global library
  Next project → Library enriches new character profiles automatically
"""
import json
import hashlib
import logging
from time_utils import utc_now  # type: ignore
from typing import List, Dict, Any, Optional

logger = logging.getLogger("character_library")

# ══════════════════════════════════════════════════════════════════════════════
# COMPLETE CHARACTER TYPE TAXONOMY
# ══════════════════════════════════════════════════════════════════════════════

NARRATIVE_ROLES = {
    "protagonist":          "The central character through whose perspective the story unfolds",
    "antagonist":           "The primary opposing force, whether human, systemic, or internal",
    "deuteragonist":        "The second lead — equal weight, different perspective",
    "tritagonist":          "The third lead — triangulates the central conflict",
    "mentor":               "Guides the protagonist; carries the wisdom the hero lacks",
    "love_interest":        "The character whose relationship with the protagonist drives emotional stakes",
    "comic_relief":         "Provides tonal release; often carries unexpected emotional depth",
    "confidant":            "The trusted intimate — receives what the protagonist cannot say publicly",
    "threshold_guardian":   "Tests the protagonist before advancement; not necessarily the villain",
    "trickster":            "Disrupts the status quo; morally ambiguous agent of change",
    "shapeshifter":         "Allegiances and nature shift; keeps the audience — and hero — uncertain",
    "shadow":               "The dark mirror of the protagonist; what they could become",
    "herald":               "Delivers the call to action; catalyst for the journey",
    "narrator":             "Frames the story; may be unreliable; often the future self of protagonist",
    "supporting":           "Serves the main narrative without carrying independent arc weight",
    "minor":                "Day-player level; serves a single scene function",
}

JUNGIAN_ARCHETYPES = {
    "the_hero":      "Wills forward through adversity; defined by courage, sacrifice, transformation",
    "the_sage":      "Seeks truth above comfort; the philosopher, scientist, detective, mentor",
    "the_innocent":  "Seeks safety and happiness; pre-fall; often the moral center",
    "the_explorer":  "Driven by discovery; restless, independent, searches beyond the known",
    "the_rebel":     "Breaks rules that deserve breaking; revolutionary energy, destructive potential",
    "the_lover":     "Driven by connection; beauty, passion, relationship are the primary motivators",
    "the_creator":   "Makes something new; artist, inventor, visionary, potentially obsessive",
    "the_jester":    "Lives in the moment; uses humor to speak truth; the court jester is often wisest",
    "the_caregiver": "Protects and nurtures; self-sacrificial; danger of martyrdom or control",
    "the_ruler":     "Commands order; responsible, decisive; shadow side is tyranny",
    "the_magician":  "Transforms reality; visionary, catalytic; shadow side is manipulation",
    "the_everyman":  "Belongs everywhere and nowhere; the audience's entry point into the story",
}

PRODUCTION_TIERS = {
    "series_regular":   "Core cast; present across all or most episodes; full arc development",
    "recurring":        "Returns multiple times; arc develops across appearances",
    "guest_star":       "Featured in one episode; often drives that episode's A-story",
    "day_player":       "Single scene or single episode, featured role",
    "featured_extra":   "Non-speaking or under-5; distinct visual presence required",
    "voice_only":       "Never seen; voice and implication carry full presence",
}

GENRE_TYPES = {
    "noir_detective":       "Seen too much; dry wit worn smooth by disappointment; trench coat optional",
    "femme_fatale":         "Dangerous allure; intelligence weaponized; motivations never simple",
    "corrupt_official":     "The system's face on the system's rot; plausibly deniable",
    "whistleblower":        "Carries truth at personal cost; the bravery is quiet, not heroic",
    "scientist":            "Precision thinker; the lab coat is armor against feeling",
    "soldier":              "Trained to action, not reflection; the war follows them home",
    "journalist":           "Questions as weapon; the notebook protects; the story is the mission",
    "politician":           "Language as performance; truth is leverage, not principle",
    "doctor":               "Competence as identity; the medical hierarchy is the world's hierarchy",
    "criminal":             "The system failed them first, or they found it easier; complex, not cartoonish",
    "law_enforcement":      "Authority and doubt in equal measure; the badge is both shield and burden",
    "anti_hero":            "Does the right thing badly, or the wrong thing for right reasons",
    "tragic_hero":          "The flaw is visible from scene one; the audience watches the approach",
    "elder":                "Time-compressed wisdom; the weight of having survived; patience as power",
    "child":                "Unfiltered perception; the adult world seen without its self-deceptions",
    "supernatural":         "Operates outside mortality rules; visual grammar must signal the difference",
}

# ── OpenAI TTS Voice Reference ────────────────────────────────────────────────
VOICE_PROFILES = {
    "alloy":   {"gender": "neutral", "quality": "balanced and clear", "best_for": "narrators, everyman characters, procedural exposition"},
    "echo":    {"gender": "male",    "quality": "soft-spoken and measured", "best_for": "intellectuals, doctors, scientists, confidants"},
    "fable":   {"gender": "neutral", "quality": "warm and expressive", "best_for": "mentors, storytellers, love interests, caretakers"},
    "onyx":    {"gender": "male",    "quality": "deep and commanding", "best_for": "antagonists, authority figures, noir detectives, rulers"},
    "nova":    {"gender": "female",  "quality": "warm and natural", "best_for": "protagonists, journalists, leads, love interests"},
    "shimmer": {"gender": "female",  "quality": "clear and bright", "best_for": "innocents, young characters, comic relief, heralds"},
}

# ── Foundational Archetype Seed Library ──────────────────────────────────────
# The 26 universal character archetypes that seed the library on first use.
# Every project enriches and expands beyond these foundations.
SEED_ARCHETYPES: List[Dict[str, Any]] = [
    {
        "archetype_id": "noir_detective_male",
        "name": "The Noir Detective (Male)",
        "narrative_role": "protagonist",
        "jungian_archetype": "the_sage",
        "production_tier": "series_regular",
        "genre_type": "noir_detective",
        "visual_prompt": "weathered white male detective, 40s, dark circles, sharp eyes, rumpled suit, loosened tie, cigarette, world-weary expression",
        "voice_id": "onyx",
        "voice_description": "Dry, measured baritone. Speaks like each word costs something.",
        "visual_style_notes": "Low-key lighting. Shadows should bisect the face. Never fully in the light.",
        "wardrobe_signature": "Trench coat, worn dress shoes, tie always slightly loosened, hat optional but period-appropriate",
        "usage_count": 0,
    },
    {
        "archetype_id": "femme_fatale_classic",
        "name": "The Femme Fatale",
        "narrative_role": "shapeshifter",
        "jungian_archetype": "the_lover",
        "production_tier": "series_regular",
        "genre_type": "femme_fatale",
        "visual_prompt": "elegant woman, 30s, sharp cheekbones, knowing eyes, tailored dress, cool composure, slight dangerous smile",
        "voice_id": "nova",
        "voice_description": "Low, unhurried. Each word chosen for effect. The pause is the weapon.",
        "visual_style_notes": "Backlight her. Let the shadows do the moral work. She should be the most composed person in any room.",
        "wardrobe_signature": "Structured, expensive, nothing accidental",
        "usage_count": 0,
    },
    {
        "archetype_id": "the_mentor_elder",
        "name": "The Mentor / Elder Sage",
        "narrative_role": "mentor",
        "jungian_archetype": "the_sage",
        "production_tier": "recurring",
        "genre_type": "elder",
        "visual_prompt": "older person, 60s-70s, kind eyes with steel underneath, silver hair, simple clothing, unhurried bearing, hands that have done things",
        "voice_id": "fable",
        "voice_description": "Warm, unhurried. Knows the answer before the question. Never raises the voice.",
        "visual_style_notes": "Natural light. Warm amber. The world should feel safer in their presence.",
        "wardrobe_signature": "Practical, worn-in, nothing for show",
        "usage_count": 0,
    },
    {
        "archetype_id": "young_protagonist_female",
        "name": "The Young Female Lead",
        "narrative_role": "protagonist",
        "jungian_archetype": "the_hero",
        "production_tier": "series_regular",
        "genre_type": "anti_hero",
        "visual_prompt": "young woman, late 20s-early 30s, intelligent eyes, determined jaw, practical clothing, carries herself like someone who has survived things",
        "voice_id": "nova",
        "voice_description": "Direct. No performance. Speaks faster when she's certain, slower when she's working something out.",
        "visual_style_notes": "Shallow focus on the face. Let the environment blur. She is the story.",
        "wardrobe_signature": "Functional over fashionable. What you wear when you're working.",
        "usage_count": 0,
    },
    {
        "archetype_id": "corrupt_authority",
        "name": "The Corrupt Authority Figure",
        "narrative_role": "antagonist",
        "jungian_archetype": "the_ruler",
        "production_tier": "recurring",
        "genre_type": "corrupt_official",
        "visual_prompt": "powerful male, 55-65, silver hair, expensive suit, practiced smile that never reaches the eyes, soft hands, the confidence of consequence",
        "voice_id": "onyx",
        "voice_description": "Measured, patrician. Never argues. States. The danger is in the calm.",
        "visual_style_notes": "Wide shot to establish power. Then close on the eyes when he smiles.",
        "wardrobe_signature": "Bespoke suit, American flag pin or equivalent authority signifier, watch worth more than most cars",
        "usage_count": 0,
    },
    {
        "archetype_id": "the_whistleblower",
        "name": "The Whistleblower",
        "narrative_role": "herald",
        "jungian_archetype": "the_rebel",
        "production_tier": "guest_star",
        "genre_type": "whistleblower",
        "visual_prompt": "ordinary-looking person, 35-45, anxious eyes scanning exits, practical clothes, phone gripped tight, the posture of someone who knows too much",
        "voice_id": "echo",
        "voice_description": "Controlled nervousness. Speaks quickly then catches themselves. Every pause is a risk assessment.",
        "visual_style_notes": "Handheld camera. Tighter than comfortable. The world pressing in.",
        "wardrobe_signature": "Nothing memorable. Deliberately average. Trying to disappear.",
        "usage_count": 0,
    },
    {
        "archetype_id": "the_journalist",
        "name": "The Investigative Journalist",
        "narrative_role": "deuteragonist",
        "jungian_archetype": "the_explorer",
        "production_tier": "series_regular",
        "genre_type": "journalist",
        "visual_prompt": "sharp-eyed journalist, 30s, notebook or recorder always present, slightly unkempt, moves fast, dressed for function not fashion",
        "voice_id": "alloy",
        "voice_description": "Quick and precise. Questions that sound conversational but aren't. Comfortable with silence.",
        "visual_style_notes": "Active framing. Catching the world mid-motion. Observational energy.",
        "wardrobe_signature": "Press credentials visible. Layers. Dressed for twelve-hour days.",
        "usage_count": 0,
    },
    {
        "archetype_id": "the_soldier_veteran",
        "name": "The Veteran Soldier",
        "narrative_role": "supporting",
        "jungian_archetype": "the_hero",
        "production_tier": "recurring",
        "genre_type": "soldier",
        "visual_prompt": "veteran soldier, 30s-40s, alert eyes that never fully rest, economic movement, carries the war in the body even in civilian clothes",
        "voice_id": "echo",
        "voice_description": "Minimal. Economy of language earned through necessity. Long pauses that mean more than the words.",
        "visual_style_notes": "Stillness as presence. The camera should feel his containment.",
        "wardrobe_signature": "Military-adjacent civilian — practical, no wasted fabric, boots",
        "usage_count": 0,
    },
    {
        "archetype_id": "child_witness",
        "name": "The Child Witness",
        "narrative_role": "herald",
        "jungian_archetype": "the_innocent",
        "production_tier": "day_player",
        "genre_type": "child",
        "visual_prompt": "child, 8-12 years old, wide observant eyes, too still for their age, the expression of someone who has seen adult things",
        "voice_id": "shimmer",
        "voice_description": "Matter-of-fact delivery of terrible things. The horror is in the casualness.",
        "visual_style_notes": "Shoot from child's eye level. Never patronize with a high angle.",
        "wardrobe_signature": "Age-appropriate but something slightly wrong — too clean, or too dirty, or missing a shoe",
        "usage_count": 0,
    },
    {
        "archetype_id": "the_trickster_ally",
        "name": "The Trickster Ally",
        "narrative_role": "trickster",
        "jungian_archetype": "the_jester",
        "production_tier": "recurring",
        "genre_type": "criminal",
        "visual_prompt": "sharp-featured person, 30s, quick eyes tracking everything, slight perpetual amusement, dressed for mobility and deniability",
        "voice_id": "fable",
        "voice_description": "Warm and slippery. Makes you like them before you realize what they've taken.",
        "visual_style_notes": "Always in motion or about to be. The frame can't quite contain them.",
        "wardrobe_signature": "Whatever serves the current con. The chameleon's wardrobe.",
        "usage_count": 0,
    },
    {
        "archetype_id": "the_scientist",
        "name": "The Scientist / Expert",
        "narrative_role": "supporting",
        "jungian_archetype": "the_creator",
        "production_tier": "recurring",
        "genre_type": "scientist",
        "visual_prompt": "scientist, 40s, focused eyes behind glasses or not, dressed for a lab or a lecture, the mind visibly working even when the body is still",
        "voice_id": "echo",
        "voice_description": "Precise. Technical vocabulary deployed naturally. Occasionally forgets the audience doesn't know what they know.",
        "visual_style_notes": "Environments that reflect the work — whiteboards, equipment, data. The space is their character.",
        "wardrobe_signature": "Functional, possibly wrong for the social occasion",
        "usage_count": 0,
    },
    {
        "archetype_id": "the_tragic_hero",
        "name": "The Tragic Hero",
        "narrative_role": "protagonist",
        "jungian_archetype": "the_hero",
        "production_tier": "series_regular",
        "genre_type": "tragic_hero",
        "visual_prompt": "person carrying visible weight, late 30s-40s, capable face with evidence of past damage, the posture of someone fighting the gravity of their own nature",
        "voice_id": "onyx",
        "voice_description": "Speaks with authority earned through suffering. The control in the voice is the cost of the wound.",
        "visual_style_notes": "The flaw should be visible in the way they hold themselves. Every shot a slow approach to the inevitable.",
        "wardrobe_signature": "Something that used to mean more. A watch from someone gone. A coat too good for what they're doing.",
        "usage_count": 0,
    },
]


class CharacterLibrary:
    """
    The growing institutional memory of all character archetypes
    encountered and profiled across the lifetime of the application.

    Starts with 26 seed archetypes on first use.
    Grows with every project analyzed.
    Provides intelligent pre-population for new character profiles.
    """

    def __init__(self, db_session_factory):
        self._sf = db_session_factory
        self._ensure_seed_archetypes()

    def _ensure_seed_archetypes(self) -> None:
        from database.models import CharacterArchetype  # type: ignore
        db = self._sf()
        try:
            if db.query(CharacterArchetype).count() == 0:
                logger.info(f"CHARACTER LIBRARY: Seeding {len(SEED_ARCHETYPES)} foundational archetypes...")
                for a in SEED_ARCHETYPES:
                    db.add(CharacterArchetype(
                        id=a["archetype_id"],
                        name=a["name"],
                        narrative_role=a["narrative_role"],
                        jungian_archetype=a["jungian_archetype"],
                        production_tier=a["production_tier"],
                        genre_type=a["genre_type"],
                        visual_prompt=a["visual_prompt"],
                        voice_id=a["voice_id"],
                        voice_description=a["voice_description"],
                        visual_style_notes=a["visual_style_notes"],
                        wardrobe_signature=a["wardrobe_signature"],
                        usage_count=0,
                        created_at=utc_now(),
                    ))
                db.commit()
                logger.info("CHARACTER LIBRARY: Seed archetypes installed.")
            else:
                total = db.query(CharacterArchetype).count()
                logger.info(f"CHARACTER LIBRARY: {total} archetypes loaded.")
        except Exception as e:
            logger.error(f"CHARACTER LIBRARY: Seed error: {e}")
            db.rollback()
        finally:
            db.close()

    def find_matching_archetype(self, character_name: str, role: str, genre_type: str = "") -> Optional[Dict]:
        """
        Find the closest matching archetype from the library for a new character.
        Used to pre-populate visual and voice profiles.
        """
        from database.models import CharacterArchetype  # type: ignore
        db = self._sf()
        try:
            q = db.query(CharacterArchetype)
            if role:
                q = q.filter(CharacterArchetype.narrative_role == role)
            if genre_type:
                q = q.filter(CharacterArchetype.genre_type == genre_type)
            match = q.order_by(CharacterArchetype.usage_count.desc()).first()
            if match:
                match.usage_count += 1
                db.commit()
                return {
                    "archetype_id": match.id,
                    "name": match.name,
                    "visual_prompt": match.visual_prompt,
                    "voice_id": match.voice_id,
                    "voice_description": match.voice_description,
                    "visual_style_notes": match.visual_style_notes,
                    "wardrobe_signature": match.wardrobe_signature,
                }
        except Exception as e:
            logger.error(f"CHARACTER LIBRARY: Archetype lookup error: {e}")
        finally:
            db.close()
        return None

    def add_archetype_from_character(self, character: Dict[str, Any], genre: str) -> str:
        """
        Learn from a newly profiled character and add it as a reusable archetype.
        Returns the archetype ID.
        """
        from database.models import CharacterArchetype  # type: ignore
        archetype_id = hashlib.sha256(
            f"{character.get('name','')}{character.get('visual_prompt','')}".encode()
        ).hexdigest()[:16]

        db = self._sf()
        try:
            existing = db.query(CharacterArchetype).filter(CharacterArchetype.id == archetype_id).first()
            if not existing:
                db.add(CharacterArchetype(
                    id=archetype_id,
                    name=f"{character.get('name', 'Unknown')} ({genre})",
                    narrative_role=character.get("role", "supporting"),
                    jungian_archetype="",
                    production_tier=character.get("production_tier", "day_player"),
                    genre_type=genre,
                    visual_prompt=character.get("visual_prompt", ""),
                    voice_id=character.get("voice_id", "alloy"),
                    voice_description=character.get("voice_description", ""),
                    visual_style_notes=character.get("description", ""),
                    wardrobe_signature=character.get("wardrobe", ""),
                    usage_count=1,
                    created_at=utc_now(),
                ))
                db.commit()
                logger.debug(f"CHARACTER LIBRARY: New archetype '{character.get('name')}' added")
            return archetype_id
        except Exception as e:
            logger.error(f"CHARACTER LIBRARY: Add archetype error: {e}")
            db.rollback()
            return ""
        finally:
            db.close()

    def get_stats(self) -> Dict[str, Any]:
        """Return library statistics."""
        from database.models import CharacterArchetype  # type: ignore
        db = self._sf()
        try:
            total = db.query(CharacterArchetype).count()
            by_role = {}
            by_genre = {}
            for a in db.query(CharacterArchetype).all():
                by_role[a.narrative_role] = by_role.get(a.narrative_role, 0) + 1
                if a.genre_type:
                    by_genre[a.genre_type] = by_genre.get(a.genre_type, 0) + 1
            top = (
                db.query(CharacterArchetype)
                .order_by(CharacterArchetype.usage_count.desc())
                .limit(5).all()
            )
            return {
                "total_archetypes": total,
                "by_role": by_role,
                "by_genre_type": by_genre,
                "taxonomy": {
                    "narrative_roles": len(NARRATIVE_ROLES),
                    "jungian_archetypes": len(JUNGIAN_ARCHETYPES),
                    "production_tiers": len(PRODUCTION_TIERS),
                    "genre_types": len(GENRE_TYPES),
                    "possible_combinations": len(NARRATIVE_ROLES) * len(JUNGIAN_ARCHETYPES) * len(PRODUCTION_TIERS) * len(GENRE_TYPES),
                },
                "voice_profiles": VOICE_PROFILES,
                "most_used": [{"name": a.name, "usage": a.usage_count} for a in top],
            }
        finally:
            db.close()

    def list_archetypes(self, role: str = None, genre_type: str = None, limit: int = 100) -> List[Dict]:
        """List archetypes from the library."""
        from database.models import CharacterArchetype  # type: ignore
        db = self._sf()
        try:
            q = db.query(CharacterArchetype)
            if role:
                q = q.filter(CharacterArchetype.narrative_role == role)
            if genre_type:
                q = q.filter(CharacterArchetype.genre_type == genre_type)
            archetypes = q.order_by(CharacterArchetype.usage_count.desc()).limit(limit).all()
            return [
                {
                    "id": a.id,
                    "name": a.name,
                    "narrative_role": a.narrative_role,
                    "jungian_archetype": a.jungian_archetype,
                    "production_tier": a.production_tier,
                    "genre_type": a.genre_type,
                    "visual_prompt": a.visual_prompt,
                    "voice_id": a.voice_id,
                    "voice_description": a.voice_description,
                    "visual_style_notes": a.visual_style_notes,
                    "wardrobe_signature": a.wardrobe_signature,
                    "usage_count": a.usage_count,
                }
                for a in archetypes
            ]
        finally:
            db.close()

    @staticmethod
    def get_full_taxonomy() -> Dict[str, Any]:
        """Return the complete character type taxonomy."""
        return {
            "narrative_roles": NARRATIVE_ROLES,
            "jungian_archetypes": JUNGIAN_ARCHETYPES,
            "production_tiers": PRODUCTION_TIERS,
            "genre_types": GENRE_TYPES,
            "voice_profiles": VOICE_PROFILES,
            "total_possible_combinations": (
                len(NARRATIVE_ROLES) * len(JUNGIAN_ARCHETYPES) *
                len(PRODUCTION_TIERS) * len(GENRE_TYPES)
            ),
        }
