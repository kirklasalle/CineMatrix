"""
Unit tests for StoryDoctor & Beat Sheet Analyzer (Phase 5).
Validates 15-beat mappings, tension arc calculation, and coverage generation.
"""
import pytest
from backend.story_doctor import StoryDoctor, BLAKE_SNYDER_BEATS


def test_blake_snyder_beats_structure():
    assert len(BLAKE_SNYDER_BEATS) == 15
    beat_ids = [b["id"] for b in BLAKE_SNYDER_BEATS]
    assert "opening_image" in beat_ids
    assert "catalyst" in beat_ids
    assert "midpoint" in beat_ids
    assert "all_hope_is_lost" in beat_ids
    assert "finale" in beat_ids
    assert "final_image" in beat_ids


def test_analyze_beat_sheet_mapping():
    scenes = [
        {"scene_number": i + 1, "heading": f"INT. SCENE {i+1} - DAY", "content": f"Dialogue and action for scene {i+1}"}
        for i in range(15)
    ]
    frames = [
        {"scene_number": i + 1, "intensity_score": 5.0 + (i % 5), "intensity_type": "Action Peak"}
        for i in range(15)
    ]

    analysis = StoryDoctor.analyze_beat_sheet(scenes, frames)
    assert analysis["total_scenes"] == 15
    assert len(analysis["beats"]) == 15
    assert analysis["act_distribution"]["act_1"] > 0
    assert analysis["act_distribution"]["act_2a"] > 0
    assert analysis["act_distribution"]["act_3"] > 0


def test_calculate_narrative_arc():
    scenes = [{"scene_number": 1, "heading": "INT. OFFICE"}, {"scene_number": 2, "heading": "EXT. STREET"}]
    frames = [{"scene_number": 1, "intensity_score": 4.0}, {"scene_number": 2, "intensity_score": 8.5}]

    arc = StoryDoctor.calculate_narrative_arc(scenes, frames)
    assert len(arc) == 2
    assert arc[0]["tension_score"] == 4.0
    assert arc[1]["tension_score"] == 8.5
    assert "phase" in arc[0]


def test_generate_coverage_summary():
    scenes = [{"scene_number": 1, "heading": "INT. ROOM"}]
    coverage = StoryDoctor.generate_coverage_summary(
        project_name="Noir Film",
        scenes=scenes,
        characters=[{"name": "HARRIS", "is_lead": True}],
    )
    assert coverage["title"] == "Noir Film"
    assert coverage["lead_characters"] == ["HARRIS"]
    assert "pacing_grade" in coverage
    assert len(coverage["strengths"]) > 0
