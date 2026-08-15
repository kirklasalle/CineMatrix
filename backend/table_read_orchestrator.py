"""
Storyboard AI — Virtual Table Read Orchestrator (Phase 7).
Extracts dialogue cues, synthesizes multi-voice audio with cadence pauses,
and generates synchronized timestamps for teleprompter script reading.
"""
import re
import io
import os
import base64
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

AUDIO_DIR = Path(__file__).parent / "static" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


class TableReadOrchestrator:
    """Orchestrates multi-character virtual screenplay table reads."""

    @staticmethod
    def extract_dialogue_cues(scene_text: str) -> List[Dict[str, Any]]:
        """
        Parses screenplay scene text into structured dialogue cues and narrative descriptions.
        """
        cues = []
        lines = scene_text.split("\n")
        current_speaker = None
        current_dialogue = []

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                if current_speaker and current_dialogue:
                    cues.append({
                        "type": "dialogue",
                        "character": current_speaker,
                        "text": " ".join(current_dialogue),
                    })
                    current_speaker = None
                    current_dialogue = []
                continue

            # Check if line is a Character Cue (ALL CAPS, short, not scene heading)
            if (
                trimmed.isupper()
                and len(trimmed) < 30
                and not trimmed.startswith("INT.")
                and not trimmed.startswith("EXT.")
                and not trimmed.startswith("CUT TO")
                and not trimmed.startswith("FADE")
            ):
                if current_speaker and current_dialogue:
                    cues.append({
                        "type": "dialogue",
                        "character": current_speaker,
                        "text": " ".join(current_dialogue),
                    })
                    current_dialogue = []

                # Clean parentheticals e.g. HARRIS (V.O.) -> HARRIS
                clean_char = re.sub(r'\(.*?\)', '', trimmed).strip()
                current_speaker = clean_char
            elif current_speaker:
                # Accumulate dialogue
                if not (trimmed.startswith("(") and trimmed.endswith(")")):
                    current_dialogue.append(trimmed)
            else:
                # Narrator / Action block
                if len(trimmed) > 15:
                    cues.append({
                        "type": "action",
                        "character": "NARRATOR",
                        "text": trimmed,
                    })

        if current_speaker and current_dialogue:
            cues.append({
                "type": "dialogue",
                "character": current_speaker,
                "text": " ".join(current_dialogue),
            })

        # If no strict cues were detected, chunk text as narrative lines
        if not cues:
            chunks = [c.strip() for c in scene_text.split(". ") if len(c.strip()) > 10]
            for ch in chunks:
                cues.append({
                    "type": "action",
                    "character": "NARRATOR",
                    "text": ch + ".",
                })

        return cues

    @staticmethod
    def generate_timeline_timestamps(cues: List[Dict[str, Any]], pause_seconds: float = 0.4) -> List[Dict[str, Any]]:
        """
        Calculates estimated synchronized timeline timestamps based on speech cadence (~150 WPM).
        """
        timeline = []
        current_time = 0.0

        for cue in cues:
            words = len(cue["text"].split())
            # Estimate speech duration: ~150 words per minute = 2.5 words/sec
            duration = max(1.5, round(words / 2.5, 2))
            start_time = round(current_time, 2)
            end_time = round(current_time + duration, 2)

            timeline.append({
                "character": cue["character"],
                "type": cue["type"],
                "text": cue["text"],
                "start_time": start_time,
                "end_time": end_time,
                "duration": duration,
            })

            current_time = end_time + pause_seconds

        return timeline
