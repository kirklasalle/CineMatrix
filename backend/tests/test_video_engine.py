"""
Unit tests for VideoEngine (Phase 4).
Validates animatic video generation, presets, and master video reel compilation.
"""
import os
import pytest
from backend.video_engine import VideoEngine, MOTION_PRESETS


def test_motion_presets_complete():
    assert len(MOTION_PRESETS) >= 6
    expected = ["dolly_in", "dolly_out", "pan_left", "pan_right", "handheld", "slow_motion"]
    for key in expected:
        assert key in MOTION_PRESETS
        preset = MOTION_PRESETS[key]
        assert "name" in preset
        assert "zoom_start" in preset
        assert "zoom_end" in preset


def test_generate_frame_animatic_local():
    """Verify that generate_frame_animatic creates a valid .mp4 file."""
    output_path = VideoEngine.generate_frame_animatic(
        image_source=None,  # Uses built-in cinematic placeholder
        motion_preset="dolly_in",
        duration=1.0,
        fps=12,
        width=320,
        height=180,
    )
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 1000
    assert output_path.endswith(".mp4")


def test_compile_master_reel():
    """Verify that compile_master_reel stitches frames into a master video reel."""
    frames = [
        {
            "scene_number": 1,
            "heading": "INT. COFFEE SHOP - DAY",
            "shot_type": "MEDIUM CLOSE-UP",
            "image_path": None,
            "motion_preset": "dolly_in",
        },
        {
            "scene_number": 2,
            "heading": "EXT. RAINY STREET - NIGHT",
            "shot_type": "WIDE SHOT",
            "image_path": None,
            "motion_preset": "pan_left",
        },
    ]

    video_bytes = VideoEngine.compile_master_reel(
        project_name="Test Production",
        frames=frames,
        fps=12,
        width=320,
        height=180,
    )
    assert isinstance(video_bytes, bytes)
    assert len(video_bytes) > 2000
