"""
Cinematic Knowledge Base — The Second Brain of Storyboard AI.

A dynamic, self-growing repository of cinematic wisdom that accumulates
knowledge from every script analyzed, every storyboard generated, and every
visual pattern observed. It preserves the integrity of:

  — Cinema and its visual grammar
  — Storytelling and narrative architecture
  — Journalism and factual authenticity
  — Production values and professional craft
  — The authentic voice of every genre

The KB learns from processed material, enriches future analyses with
accumulated domain wisdom, and serves as the institutional memory of the
Storyboard AI system.

Architecture:
  - SQLite-backed persistent knowledge entries
  - LLM-powered insight extraction from each analysis batch
  - Semantic tagging and cross-referencing by genre/style/theme
  - Usage tracking (which insights prove most valuable)
  - Confidence scoring and temporal decay for stale knowledge
"""
import logging
import json
from time_utils import utc_now  # type: ignore
import hashlib
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

logger = logging.getLogger("knowledge_base")


# ── Knowledge Entry Types ─────────────────────────────────────────────────────
class KnowledgeType:
    CINEMATOGRAPHY   = "cinematography"   # Camera, lighting, lens insights
    NARRATIVE        = "narrative"        # Story structure, beat patterns
    VISUAL_STYLE     = "visual_style"     # Genre-style visual relationships
    PRODUCTION       = "production"       # Production design, set dressing
    CHARACTER        = "character"        # Visual archetype patterns
    GENRE_PATTERN    = "genre_pattern"    # Genre-specific recurring motifs
    TECHNICAL        = "technical"        # Technical craft observations
    EMOTIONAL        = "emotional"        # Emotional staging patterns
    AUTHENTICITY     = "authenticity"     # Factual/journalistic accuracy notes
    INDUSTRY         = "industry"        # Industry standard practices


SEED_WISDOM: List[Dict[str, Any]] = [
    # ── Cinematography ──────────────────────────────────────────────────
    {
        "type": KnowledgeType.CINEMATOGRAPHY,
        "title": "The Rule of the Close-Up",
        "content": (
            "A close-up communicates interiority. Use it when words fail and the face "
            "must carry the entire emotional weight of the scene. Bergman, Dreyer, and "
            "Leone built careers on this single principle."
        ),
        "genre": "drama",
        "tags": ["close-up", "emotion", "face", "interiority"],
        "source": "Seed Wisdom",
        "confidence": 0.98,
    },
    {
        "type": KnowledgeType.CINEMATOGRAPHY,
        "title": "Deep Focus and Democratic Space",
        "content": (
            "Deep focus (f/22+) gives every element of the frame equal visual weight — "
            "it is a democratic camera. Welles and Toland used it to implicate the "
            "environment as an active character, not mere background. Consider when "
            "the setting should speak with equal authority to the actor."
        ),
        "genre": "drama",
        "tags": ["deep-focus", "Welles", "Toland", "environment", "composition"],
        "source": "Seed Wisdom",
        "confidence": 0.97,
    },
    {
        "type": KnowledgeType.CINEMATOGRAPHY,
        "title": "The Dutch Angle and Psychological Instability",
        "content": (
            "A Dutch tilt (canted frame) signals that the world itself is wrong. "
            "Reserve it for moments of genuine moral or psychological disorientation — "
            "overuse destroys its power. Carol Reed used it surgically in The Third Man "
            "to externalize moral corruption through camera geometry."
        ),
        "genre": "thriller",
        "tags": ["dutch-angle", "tilt", "instability", "psychology", "Reed"],
        "source": "Seed Wisdom",
        "confidence": 0.96,
    },
    # ── Narrative ───────────────────────────────────────────────────────
    {
        "type": KnowledgeType.NARRATIVE,
        "title": "The Three-Act Tension Architecture",
        "content": (
            "Act I establishes the world and the wound. Act II is the crucible where "
            "the wound is tested. Act III is either the scar or the healing. Every "
            "storyboard frame should implicitly know which act it lives in — the "
            "visual grammar changes accordingly: wider in Act I, tighter in III."
        ),
        "genre": "drama",
        "tags": ["three-act", "structure", "narrative", "framing"],
        "source": "Seed Wisdom",
        "confidence": 0.99,
    },
    {
        "type": KnowledgeType.NARRATIVE,
        "title": "The Inciting Visual — The First Lie",
        "content": (
            "The inciting incident deserves a frame that establishes the visual contract "
            "with the audience. Whatever the film promises visually here, it must deliver "
            "or deliberately subvert at the climax. The storyboard artist's job is to "
            "plant the visual motif that will pay off."
        ),
        "genre": "all",
        "tags": ["inciting-incident", "motif", "visual-contract", "foreshadowing"],
        "source": "Seed Wisdom",
        "confidence": 0.95,
    },
    # ── Genre Patterns ───────────────────────────────────────────────────
    {
        "type": KnowledgeType.GENRE_PATTERN,
        "title": "Noir's Geometry of Entrapment",
        "content": (
            "In noir, the frame is always a trap. Characters are framed through doorways, "
            "behind bars of shadow, hemmed by architecture. The visual grammar of noir "
            "communicates that escape is impossible before a single line of dialogue. "
            "Venetian blind shadows are the bars of fate."
        ),
        "genre": "noir",
        "tags": ["noir", "entrapment", "shadow", "geometry", "fatalism"],
        "source": "Seed Wisdom",
        "confidence": 0.97,
    },
    {
        "type": KnowledgeType.GENRE_PATTERN,
        "title": "Horror's Empty Room Problem",
        "content": (
            "The most frightening horror shot is often an empty room. The anticipation "
            "of threat exceeds the threat itself. Hitchcock's 'refrigerator' theory: "
            "if you show the bomb under the table, a mundane conversation becomes "
            "unbearable tension. Show the viewer what the character cannot see."
        ),
        "genre": "horror",
        "tags": ["horror", "anticipation", "dread", "Hitchcock", "negative-space"],
        "source": "Seed Wisdom",
        "confidence": 0.97,
    },
    # ── Production Values ─────────────────────────────────────────────────
    {
        "type": KnowledgeType.PRODUCTION,
        "title": "Production Design as Character Biography",
        "content": (
            "A character's living space is their psychological portrait. Fincher fills "
            "rooms with evidence of obsession. Anderson populates them with miniaturized "
            "ambition. Kubrick strips them to institutional geometry. The storyboard "
            "artist must read the production design as biography."
        ),
        "genre": "drama",
        "tags": ["production-design", "character", "environment", "Fincher", "Anderson", "Kubrick"],
        "source": "Seed Wisdom",
        "confidence": 0.94,
    },
    # ── Visual Style ───────────────────────────────────────────────────────
    {
        "type": KnowledgeType.VISUAL_STYLE,
        "title": "Color as Emotional Architecture",
        "content": (
            "The color palette is the film's emotional contract. Warm amber signals "
            "memory, safety, or nostalgia. Cool blue signals isolation, technology, "
            "or threat. Green signals corruption, illness, or the uncanny. The "
            "storyboard artist who understands this can write emotion in color alone."
        ),
        "genre": "all",
        "tags": ["color", "palette", "emotion", "amber", "blue", "green"],
        "source": "Seed Wisdom",
        "confidence": 0.96,
    },
    # ── Authenticity ───────────────────────────────────────────────────────
    {
        "type": KnowledgeType.AUTHENTICITY,
        "title": "The Cost of the Fake Detail",
        "content": (
            "One anachronistic prop, one wrongly-labeled street sign, one impossible "
            "sightline — any single factual error breaks the audience's trust contract "
            "permanently. Research is not optional; it is the foundation of cinematic "
            "authenticity. The storyboard is the first line of continuity defense."
        ),
        "genre": "period",
        "tags": ["authenticity", "research", "continuity", "period", "detail"],
        "source": "Seed Wisdom",
        "confidence": 0.99,
    },
    # ── Emotional ─────────────────────────────────────────────────────────
    {
        "type": KnowledgeType.EMOTIONAL,
        "title": "Silence as the Loudest Instrument",
        "content": (
            "The pause before the answer. The held breath before the kiss. The beat "
            "of stillness before violence. Cinema's most powerful emotional instrument "
            "is not movement — it is the charged absence of movement. The storyboard "
            "frame that holds stillness earns the cut that follows."
        ),
        "genre": "drama",
        "tags": ["silence", "pause", "stillness", "timing", "emotion"],
        "source": "Seed Wisdom",
        "confidence": 0.98,
    },
    {
        "type": KnowledgeType.NARRATIVE,
        "title": "The Three Levels of Story Quality",
        "content": (
            "Level 1: The audience knows what happened. "
            "Level 2: The audience feels the tension. "
            "Level 3: The audience carries something home. "
            "The distance from Level 1 to Level 3 is not vocabulary or technique — "
            "it is specificity earned by observation, subtext earned by trusting the reader, "
            "and the image that does the work the words no longer need to."
        ),
        "genre": "all",
        "tags": ["craft", "quality", "levels", "specificity", "subtext", "image"],
        "source": "ACS4.6 — Quality Spectrum",
        "confidence": 1.0,
    },
    {
        "type": KnowledgeType.CINEMATOGRAPHY,
        "title": "The Final Image is the Scene's Real Last Line",
        "content": (
            "In great cinema, the final image of a scene says what the dialogue was "
            "building toward but could not say directly. A cup of coffee steaming at "
            "an empty seat. A door slowly closing. A hand opening and then not. "
            "The writer's job is to build toward this image; the storyboard artist's "
            "job is to recognize it and make it the frame."
        ),
        "genre": "all",
        "tags": ["final-image", "visual-conclusion", "scene-ending", "subtext", "symbolism"],
        "source": "ACS4.6 — Quality Spectrum",
        "confidence": 0.99,
    },
    {
        "type": KnowledgeType.TECHNICAL,
        "title": "The Empty Seat — Objects as Absent Characters",
        "content": (
            "The most powerful presences in cinema are sometimes absences. "
            "An empty chair, a half-eaten meal, a coat on a hook — these carry "
            "the full weight of whoever is not in them. The storyboard artist "
            "who understands this will always find the most powerful frame "
            "is often the one without the character in it."
        ),
        "genre": "drama",
        "tags": ["absence", "objects", "empty-space", "grief", "presence"],
        "source": "ACS4.6 — Quality Spectrum",
        "confidence": 0.99,
    },
]


class CinematicKnowledgeBase:
    """
    The Second Brain of Storyboard AI.

    Manages a growing, dynamic knowledge repository of cinematic wisdom.
    Learns from every script analyzed. Enriches every analysis with
    accumulated domain expertise. Preserves the integrity of authentic,
    professional storytelling craft.
    """

    def __init__(self, db_session_factory):
        self._session_factory = db_session_factory
        self._ensure_seed_wisdom()

    def _ensure_seed_wisdom(self) -> None:
        """Populate the KB with foundational cinematic wisdom on first run."""
        from database.models import KnowledgeEntry  # type: ignore
        db: Session = self._session_factory()
        try:
            existing = db.query(KnowledgeEntry).count()
            if existing == 0:
                logger.info(f"KB: Seeding foundational cinematic wisdom ({len(SEED_WISDOM)} entries)...")
                for entry in SEED_WISDOM:
                    ke = KnowledgeEntry(
                        id=self._make_id(entry["title"]),
                        knowledge_type=entry["type"],
                        title=entry["title"],
                        content=entry["content"],
                        genre=entry.get("genre", "all"),
                        tags=json.dumps(entry.get("tags", [])),
                        source=entry.get("source", "Seed Wisdom"),
                        confidence=entry.get("confidence", 0.8),
                        usage_count=0,
                        created_at=utc_now(),
                    )
                    db.add(ke)
                db.commit()
                logger.info(f"KB: Seed wisdom installed. Knowledge base is live.")
            else:
                logger.info(f"KB: Knowledge base loaded. {existing} entries available.")
        except Exception as e:
            logger.error(f"KB: Error during seed wisdom initialization: {e}")
            db.rollback()
        finally:
            db.close()

    def _make_id(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    def learn(
        self,
        knowledge_type: str,
        title: str,
        content: str,
        genre: str = "all",
        tags: Optional[List[str]] = None,
        source: str = "Analysis",
        confidence: float = 0.75,
    ) -> str:
        """
        Add a new insight to the knowledge base.
        Returns the ID of the created entry.
        """
        from database.models import KnowledgeEntry  # type: ignore
        entry_id = self._make_id(title + content[:32])
        db: Session = self._session_factory()
        try:
            existing = db.query(KnowledgeEntry).filter(KnowledgeEntry.id == entry_id).first()
            if existing:
                existing.usage_count += 1
                existing.confidence = min(1.0, existing.confidence + 0.02)
                db.commit()
                logger.debug(f"KB: Reinforced existing entry '{title}' (confidence={existing.confidence:.2f})")
                return entry_id

            ke = KnowledgeEntry(
                id=entry_id,
                knowledge_type=knowledge_type,
                title=title,
                content=content,
                genre=genre,
                tags=json.dumps(tags or []),
                source=source,
                confidence=confidence,
                usage_count=0,
                created_at=utc_now(),
            )
            db.add(ke)
            db.commit()
            logger.info(f"KB: Learned new insight — [{knowledge_type.upper()}] '{title}' (genre={genre})")
            return entry_id
        except Exception as e:
            logger.error(f"KB: Error learning insight '{title}': {e}")
            db.rollback()
            return ""
        finally:
            db.close()

    def recall(
        self,
        genre: str = "all",
        knowledge_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant knowledge entries for enriching an analysis.
        Returns entries sorted by confidence * usage_count (wisdom score).
        """
        from database.models import KnowledgeEntry  # type: ignore
        db: Session = self._session_factory()
        try:
            query = db.query(KnowledgeEntry)
            # Genre filter: include genre-specific AND universal entries
            if genre and genre != "all":
                query = query.filter(
                    (KnowledgeEntry.genre == genre) | (KnowledgeEntry.genre == "all")
                )
            if knowledge_type:
                query = query.filter(KnowledgeEntry.knowledge_type == knowledge_type)

            entries = query.all()

            # Score: confidence × log(1 + usage_count) — reward proven wisdom
            import math
            def wisdom_score(e):
                return e.confidence * math.log1p(e.usage_count + 1)

            entries.sort(key=wisdom_score, reverse=True)
            selected = entries[:limit]

            # Increment usage count for recalled entries
            for e in selected:
                e.usage_count += 1
            db.commit()

            result = []
            for e in selected:
                result.append({
                    "id": e.id,
                    "type": e.knowledge_type,
                    "title": e.title,
                    "content": e.content,
                    "genre": e.genre,
                    "tags": json.loads(e.tags or "[]"),
                    "confidence": e.confidence,
                    "source": e.source,
                })

            logger.debug(f"KB: Recalled {len(result)} entries for genre='{genre}' type='{knowledge_type}'")
            return result
        except Exception as e:
            logger.error(f"KB: Error recalling knowledge: {e}")
            return []
        finally:
            db.close()

    def get_wisdom_context(self, genre: str, scene_text: str = "") -> str:
        """
        Build a wisdom context string to inject into LLM analysis prompts.
        Pulls the most relevant knowledge for the current genre and returns
        it as formatted text that enriches the prompt.
        """
        entries = self.recall(genre=genre, limit=4)
        if not entries:
            return ""

        lines = ["CINEMATIC KNOWLEDGE BASE — Relevant Wisdom for This Analysis:"]
        for e in entries:
            lines.append(f"  [{e['type'].upper()}] {e['title']}: {e['content'][:200]}...")
        context = "\n".join(lines)
        logger.debug(f"KB: Injecting {len(entries)} wisdom entries into analysis prompt.")
        return context

    async def distill_insights_from_analysis(
        self,
        provider,
        scenes: List[Dict[str, Any]],
        frames: List[Dict[str, Any]],
        genre: str,
        script_title: str = "Untitled Script",
    ) -> int:
        """
        After analyzing a script, use the LLM to extract 3-5 new cinematic
        insights and add them to the knowledge base.
        Returns the number of new insights learned.
        """
        if not frames:
            return 0

        # Build a summary of the analysis for distillation
        sample_descriptions = [
            f"Scene {f['scene_number']} ({f.get('shot_type','')}/{f.get('camera_movement','')}): "
            f"{f.get('description','')[:150]}"
            for f in frames[:8]
        ]
        analysis_summary = "\n".join(sample_descriptions)

        prompt = f"""You are a cinematic knowledge distiller. You have just analyzed a {genre} screenplay titled "{script_title}".

Here are the key storyboard moments identified:

{analysis_summary}

TASK: Extract 3 to 5 genuine cinematic insights that a storyboard artist or cinematographer would find valuable. Each insight should be a transferable lesson about visual storytelling craft, not specific to this script alone.

Return ONLY a valid JSON array:
[
  {{
    "type": "cinematography|narrative|visual_style|genre_pattern|production|emotional|authenticity",
    "title": "Short memorable title for this insight",
    "content": "The insight itself — practical, specific, and transferable to future work (2-4 sentences)",
    "tags": ["tag1", "tag2", "tag3"],
    "confidence": 0.82
  }}
]
"""
        try:
            result_text = await provider.generate_text(prompt)
            import re
            m = re.search(r'\[[\s\S]*\]', result_text)
            if not m:
                logger.warning("KB: Could not extract insights JSON from LLM response")
                return 0

            insights = json.loads(m.group(0))
            count = 0
            for insight in insights:
                if not isinstance(insight, dict):
                    continue
                if not insight.get("title") or not insight.get("content"):
                    continue
                self.learn(
                    knowledge_type=insight.get("type", KnowledgeType.CINEMATOGRAPHY),
                    title=insight["title"],
                    content=insight["content"],
                    genre=genre,
                    tags=insight.get("tags", []),
                    source=f"Script: {script_title[:40]}",
                    confidence=float(insight.get("confidence", 0.75)),
                )
                count += 1

            logger.info(f"KB: Distilled {count} new insights from '{script_title}' ({genre})")
            return count
        except Exception as e:
            logger.error(f"KB: Insight distillation failed: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Return statistics about the current state of the knowledge base."""
        from database.models import KnowledgeEntry  # type: ignore
        db: Session = self._session_factory()
        try:
            total = db.query(KnowledgeEntry).count()
            by_type = {}
            for entry in db.query(KnowledgeEntry).all():
                t = entry.knowledge_type
                by_type[t] = by_type.get(t, 0) + 1

            top_entries = (
                db.query(KnowledgeEntry)
                .order_by(KnowledgeEntry.usage_count.desc())
                .limit(5)
                .all()
            )
            return {
                "total_entries": total,
                "by_type": by_type,
                "most_recalled": [{"title": e.title, "usage": e.usage_count, "confidence": e.confidence} for e in top_entries],
            }
        except Exception as e:
            logger.error(f"KB: Error getting stats: {e}")
            return {"total_entries": 0, "by_type": {}, "most_recalled": []}
        finally:
            db.close()

    def list_entries(
        self,
        genre: Optional[str] = None,
        knowledge_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """List knowledge entries for the API."""
        from database.models import KnowledgeEntry  # type: ignore
        db: Session = self._session_factory()
        try:
            q = db.query(KnowledgeEntry)
            if genre:
                q = q.filter((KnowledgeEntry.genre == genre) | (KnowledgeEntry.genre == "all"))
            if knowledge_type:
                q = q.filter(KnowledgeEntry.knowledge_type == knowledge_type)
            entries = q.order_by(KnowledgeEntry.usage_count.desc()).limit(limit).all()
            return [
                {
                    "id": e.id,
                    "type": e.knowledge_type,
                    "title": e.title,
                    "content": e.content,
                    "genre": e.genre,
                    "tags": json.loads(e.tags or "[]"),
                    "confidence": e.confidence,
                    "usage_count": e.usage_count,
                    "source": e.source,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                }
                for e in entries
            ]
        except Exception as e:
            logger.error(f"KB: Error listing entries: {e}")
            return []
        finally:
            db.close()
