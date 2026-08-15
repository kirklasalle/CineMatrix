"""
Unit tests for TableReadOrchestrator (Phase 7).
Validates screenplay dialogue cue extraction and synchronized timeline generation.
"""
import pytest
from backend.table_read_orchestrator import TableReadOrchestrator


def test_extract_dialogue_cues():
    scene_text = """
INT. DETECTIVE OFFICE - NIGHT

Rain lashes against the window. HARRIS sits behind a cluttered wooden desk.

HARRIS
(lighting a cigarette)
I told you never to come back here.

SARAH
I didn't have a choice. They found the ledger.

Harris pauses, staring at the amber flame.
"""

    cues = TableReadOrchestrator.extract_dialogue_cues(scene_text)
    assert len(cues) >= 3

    # Check character names
    speakers = [c["character"] for c in cues if c["type"] == "dialogue"]
    assert "HARRIS" in speakers
    assert "SARAH" in speakers

    # Check narrator lines
    narrators = [c for c in cues if c["type"] == "action"]
    assert len(narrators) >= 1


def test_generate_timeline_timestamps():
    cues = [
        {"type": "action", "character": "NARRATOR", "text": "The wind howls outside the deserted lodge."},
        {"type": "dialogue", "character": "HARRIS", "text": "Did you lock the cellar door?"},
        {"type": "dialogue", "character": "SARAH", "text": "It was already open."},
    ]

    timeline = TableReadOrchestrator.generate_timeline_timestamps(cues, pause_seconds=0.5)
    assert len(timeline) == 3
    assert timeline[0]["start_time"] == 0.0
    assert timeline[1]["start_time"] > timeline[0]["end_time"]
    assert timeline[2]["start_time"] > timeline[1]["end_time"]
