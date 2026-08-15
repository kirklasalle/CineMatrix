from typing import List, Dict, Any, Optional
from providers.base_provider import BaseProvider  # type: ignore
from genre_vault import get_style_guidance  # type: ignore
from style_vault import get_style  # type: ignore
import json
import re
import logging

logger = logging.getLogger("storyboard.engine")

class StoryboardEngine:
    def __init__(self, provider: BaseProvider, knowledge_base=None):
        self.provider = provider
        self.knowledge_base = knowledge_base  # Optional CinematicKnowledgeBase

    def _extract_json(self, text: str) -> str:
        """Robustly extract a JSON object from LLM output regardless of wrapper format."""
        # Fenced code block: ```json ... ``` or ``` ... ```
        m = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
        # XML-style tags
        m = re.search(r'<json>([\s\S]*?)</json>', text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
        # Raw outermost JSON object
        m = re.search(r'\{[\s\S]*\}', text)
        if m:
            return m.group(0).strip()
        return text.strip()

    async def analyze_script(
        self,
        scenes: List[Dict[str, Any]],
        user_genre: Optional[str] = None,
        storyboard_style: str = "oscar_prestige"
    ) -> List[Dict[str, Any]]:
        """Orchestrates the cinematography-aware analysis for storyboard generation."""

        # 1. Genre Detection Pass
        genre = user_genre
        if not genre:
            script_sample = "\n".join([s.get("heading", "") for s in scenes[:5]])
            genre_prompt = (
                "Analyze the following scene headings and identify the primary film genre "
                "in a single word (Action, Drama, Horror, Comedy, Thriller, SciFi, Western, "
                "Noir, Fantasy, Romance, War, Heist, Period, Psychological, Superhero, etc.):\n\n"
                f"{script_sample}"
            )
            raw_genre = await self.provider.generate_text(genre_prompt)
            genre = re.sub(r'[^a-zA-Z\-]', '', raw_genre.strip().split()[0]).lower()

        style_guidance = get_style_guidance(genre)
        visual_style = get_style(storyboard_style)
        logger.info(
            f"ENGINE: Analyzing {len(scenes)} scenes | genre='{genre}' | style='{storyboard_style}'"
        )

        # Pull relevant wisdom from the Knowledge Base
        wisdom_context = ""
        if self.knowledge_base:
            wisdom_context = self.knowledge_base.get_wisdom_context(genre)
            if wisdom_context:
                logger.debug(f"ENGINE: Knowledge base wisdom injected for genre='{genre}'")

        processed_frames = []

        # 2. Narrative & Cinematography Pass — one LLM call per scene
        for i, scene in enumerate(scenes):
            frame = await self.analyze_single_scene(
                scene=scene,
                scene_index=i,
                total_scenes=len(scenes),
                genre=genre,
                style_guidance=style_guidance,
                visual_style=visual_style,
                wisdom_context=wisdom_context,
            )
            processed_frames.append(frame)

        logger.info(f"ENGINE: Analysis complete. {len(processed_frames)} frames identified.")
        return processed_frames

    async def analyze_single_scene(
        self,
        scene: Dict[str, Any],
        scene_index: int,
        total_scenes: int,
        genre: str,
        style_guidance: Dict[str, Any],
        visual_style: Dict[str, Any],
        wisdom_context: str = "",
    ) -> Dict[str, Any]:
        """
        Analyze a single scene. Extracted so both batch and streaming
        endpoints can use the same analysis logic.
        """
        i = scene_index
        logger.info(f"ENGINE: Scene {i+1}/{total_scenes}: {scene.get('heading')}")
        logger.debug(f"ENGINE: Scene text preview: {scene.get('text','')[:120]!r}")
        scene_text = scene.get("text", "")

        prompt = f"""You are a world-class cinematographer and storyboard artist analyzing a {genre} screenplay.

Visual Style Guidance: {style_guidance['visual_style']}
Intensity Focus: {style_guidance['intensity_focus']}
Art Direction: {visual_style['name']} — {visual_style['description']}
{f"{wisdom_context}" if wisdom_context else ""}

TASK: Identify the single most cinematically powerful, storyboard-worthy moment in this scene.

Scene:
{scene.get('heading', '')}
{scene_text}

Return ONLY a valid JSON object with these exact fields — no other text:
{{
    "description": "Rich visual description for the storyboard artist: what fills the frame, action, emotion, atmosphere",
    "intensity_score": 8.5,
    "intensity_type": "Action Peak",
    "moment_summary": "One sentence explaining why this is the most powerful moment",
    "shot_type": "Low Angle Wide Shot",
    "camera_movement": "Slow dolly push-in",
    "lens": "24mm anamorphic",
    "lighting": "Hard side key light, deep shadow fill"
}}

Rules:
- intensity_score is a float from 1.0 to 10.0
- intensity_type must be exactly one of: "Action Peak", "Emotional Peak", "Lull"
- shot_type examples: ECU, CU, MCU, MS, WS, EWS, OTS, POV, Dutch Angle, Overhead
- camera_movement examples: Static, Handheld, Dolly In, Dolly Out, Pan, Tilt, Crane, Drone, Tracking
"""
        try:
            result_text = await self.provider.generate_text(prompt)
            logger.debug(f"ENGINE: Raw LLM response for scene {i+1}: {result_text[:300]!r}")
            json_text = self._extract_json(result_text)
            analysis = json.loads(json_text)
            frame = {
                "scene_number": i + 1,
                "heading": scene.get("heading", f"Scene {i + 1}"),
                "description": analysis.get("description", ""),
                "intensity_score": float(analysis.get("intensity_score", 5.0)),
                "intensity_type": analysis.get("intensity_type", "Lull"),
                "moment_summary": analysis.get("moment_summary", ""),
                "shot_type": analysis.get("shot_type", "Medium Shot"),
                "camera_movement": analysis.get("camera_movement", "Static"),
                "lens": analysis.get("lens", "50mm"),
                "lighting": analysis.get("lighting", "Natural"),
                "motion_preset": "dolly_in",
            }

            # ── Auto-Generate Visual Image for Frame ──
            try:
                visual_res = await self.generate_visual(
                    frame_description=frame["description"] or scene.get("heading", f"Scene {i+1}"),
                    genre=genre,
                    storyboard_style=visual_style.get("id", "oscar_prestige"),
                )
                frame["image_path"] = visual_res.get("image_url")
                frame["model_used"] = visual_res.get("model_used")
            except Exception as v_err:
                logger.warning(f"ENGINE: Auto-visual generation fallback for scene {i+1}: {v_err}")
                frame["image_path"] = self._get_pollinations_url(
                    f"{visual_style.get('name', 'Cinematic')} storyboard frame: {frame['description']}",
                    seed=(i + 1) * 42,
                )

            logger.info(
                f"ENGINE: Scene {i+1} ✓ | "
                f"intensity={frame['intensity_score']:.1f} | "
                f"type={frame['intensity_type']} | "
                f"shot={frame['shot_type']} | image={'✓' if frame.get('image_path') else '✗'}"
            )
            return frame
        except Exception as e:
            logger.error(f"ENGINE: Failed scene {i+1}: {e}", exc_info=True)
            fallback_desc = scene_text[:300] if scene_text else "Scene content unavailable"
            fallback_img = self._get_pollinations_url(
                f"{visual_style.get('name', 'Cinematic')} cinematic frame: {fallback_desc}",
                seed=(i + 1) * 42,
            )
            return {
                "scene_number": i + 1,
                "heading": scene.get("heading", f"Scene {i + 1}"),
                "description": fallback_desc,
                "intensity_score": 5.0,
                "intensity_type": "Lull",
                "moment_summary": "Analysis unavailable — using raw scene text",
                "shot_type": "Medium Shot",
                "camera_movement": "Static",
                "lens": "50mm",
                "lighting": "Natural",
                "image_path": fallback_img,
                "motion_preset": "dolly_in",
            }

    async def generate_visual(
        self,
        frame_description: str,
        genre: str = "drama",
        storyboard_style: str = "oscar_prestige",
        character_profiles: Optional[List[Dict[str, Any]]] = None,
    ) -> dict:
        """Generates an image for a single frame description. Returns structured result."""
        style = get_style(storyboard_style)
        style_guidance = get_style_guidance(genre.lower())

        # Build character consistency context
        char_context = ""
        if character_profiles:
            char_lines = []
            for cp in character_profiles:
                if cp.get("visual_prompt"):
                    char_lines.append(cp["visual_prompt"])
            if char_lines:
                char_context = "Character appearance consistency: " + "; ".join(char_lines) + ". "
                logger.debug(f"ENGINE: Injecting {len(char_lines)} character profiles into image prompt")

        enhanced_prompt = (
            f"{style['prompt_prefix']}. "
            f"Scene: {frame_description}. "
            f"{char_context}"
            f"Cinematography: {style_guidance['visual_style']} "
            f"Color palette: {style['color_palette']}. "
            f"Lighting: {style['lighting']}. "
            f"{style['prompt_suffix']}. "
            f"16:9 cinematic aspect ratio, professional storyboard frame quality."
        )

        # Try provider's native image generation first
        try:
            result = await self.provider.generate_image(enhanced_prompt)
            if isinstance(result, dict):
                return result
            return {
                "image_url": result,
                "model_used": "provider-default",
                "provider": self.provider.get_name(),
                "attempts": [{"model": "provider-default", "status": "success"}]
            }
        except Exception as e:
            logger.warning(f"ENGINE: Provider image generation failed ({e}), falling back to Pollinations.ai")
            attempts = getattr(e, 'attempts', [])
            attempts.append({
                "model": "Pollinations.ai (Free)",
                "status": "success",
                "note": "Free community image generation — no API key required"
            })
            pollinations_url = self._get_pollinations_url(enhanced_prompt)
            return {
                "image_url": pollinations_url,
                "model_used": "Pollinations.ai",
                "provider": "Pollinations.ai (Free Fallback)",
                "attempts": attempts
            }

    async def extract_characters(
        self,
        scenes: List[Dict[str, Any]],
        genre: str = "drama",
        script_title: str = "Untitled",
    ) -> List[Dict[str, Any]]:
        """
        Extract all named characters from parsed scenes and build visual +
        voice profiles for each. Returns a list of character dicts ready
        to be saved to the Character table.

        Each character dict contains:
          name, description, age_range, role, wardrobe, visual_prompt,
          voice_id, voice_description, first_scene, scene_count, line_count, is_lead
        """
        # Collect all character names across all scenes
        char_scene_map: Dict[str, List[int]] = {}
        for scene in scenes:
            scene_num = scene.get("scene_number", scenes.index(scene) + 1)
            for char_name in scene.get("characters", []):
                clean = char_name.strip()
                if not clean or len(clean) < 2:
                    continue
                if clean not in char_scene_map:
                    char_scene_map[clean] = []
                char_scene_map[clean].append(scene_num)

        if not char_scene_map:
            logger.info("ENGINE: No named characters found in scenes")
            return []

        logger.info(f"ENGINE: Extracting profiles for {len(char_scene_map)} characters in '{script_title}'")

        # Build a script sample for the LLM
        all_text = " ".join(s.get("text", "") for s in scenes[:12])[:3000]
        char_names = sorted(char_scene_map.keys())

        prompt = f"""You are a world-class casting director and character designer analyzing a {genre} screenplay titled "{script_title}".

The following characters appear in this script:
{chr(10).join(f"- {name} (appears in {len(char_scene_map[name])} scenes)" for name in char_names)}

Script excerpt for context:
{all_text[:2000]}

For each character, provide a detailed profile. Return ONLY a valid JSON array:
[
  {{
    "name": "CHARACTER NAME",
    "description": "Full physical appearance: height, build, age, hair, eyes, distinguishing features. Be specific and visual.",
    "age_range": "30s",
    "role": "protagonist",
    "wardrobe": "Signature clothing and style that defines this character visually",
    "visual_prompt": "Compact image-generation phrase: [gender] [age], [hair], [eyes], [build], [signature wardrobe item], [expression/energy]",
    "voice_description": "Voice quality for read-through casting: tone, accent, energy",
    "voice_id": "onyx",
    "is_lead": true
  }}
]

Rules:
- role must be one of: protagonist, antagonist, supporting, minor
- voice_id must be one of: alloy, echo, fable, onyx, nova, shimmer
  (alloy=neutral, echo=male, fable=expressive, onyx=deep male, nova=female warm, shimmer=female light)
- is_lead: true only for characters with 3+ scenes
- visual_prompt must be 15-25 words, highly specific, usable in an image generator
"""
        try:
            result_text = await self.provider.generate_text(prompt)
            json_text = re.search(r'\[[\s\S]*\]', result_text)
            if not json_text:
                logger.warning("ENGINE: Could not extract character profiles JSON")
                return self._fallback_characters(char_scene_map)

            profiles = json.loads(json_text.group(0))
            result = []
            for p in profiles:
                name = p.get("name", "").strip()
                if not name:
                    continue
                result.append({
                    "name": name,
                    "description": p.get("description", ""),
                    "age_range": p.get("age_range", ""),
                    "role": p.get("role", "supporting"),
                    "wardrobe": p.get("wardrobe", ""),
                    "visual_prompt": p.get("visual_prompt", ""),
                    "voice_description": p.get("voice_description", ""),
                    "voice_id": p.get("voice_id", "alloy"),
                    "is_lead": bool(p.get("is_lead", False)),
                    "first_scene": min(char_scene_map.get(name, [1])),
                    "scene_count": len(char_scene_map.get(name, [])),
                    "line_count": 0,  # Populated during dialogue attribution pass
                })
            logger.info(f"ENGINE: Character extraction complete — {len(result)} profiles built")
            return result
        except Exception as e:
            logger.error(f"ENGINE: Character extraction failed: {e}", exc_info=True)
            return self._fallback_characters(char_scene_map)

    def _fallback_characters(self, char_scene_map: Dict[str, List[int]]) -> List[Dict[str, Any]]:
        """Return minimal character records when LLM extraction fails."""
        voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        result = []
        for idx, (name, scenes_list) in enumerate(sorted(char_scene_map.items())):
            result.append({
                "name": name,
                "description": f"Character {name} — visual profile pending analysis",
                "age_range": "",
                "role": "protagonist" if idx == 0 else "supporting",
                "wardrobe": "",
                "visual_prompt": f"character named {name.lower()}, cinematic portrait",
                "voice_description": "",
                "voice_id": voices[idx % len(voices)],
                "is_lead": len(scenes_list) >= 3,
                "first_scene": min(scenes_list),
                "scene_count": len(scenes_list),
                "line_count": 0,
            })
        return result

    def _get_pollinations_url(self, prompt: str, seed: Optional[int] = None) -> str:
        """Generate a free high-resolution 16:9 cinematic image URL via Pollinations.ai (no API key required)."""
        import urllib.parse
        import random
        clean_prompt = prompt.strip().replace('\n', ' ').replace('  ', ' ')
        encoded = urllib.parse.quote(clean_prompt[:500])
        s = seed if seed is not None else random.randint(1000, 999999)
        return f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=576&nologo=true&seed={s}&model=flux"

