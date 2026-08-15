"""
Unit tests for GraphicNovelEngine (Phase 9).
Validates multi-panel presets, scene pagination, and 300 DPI print PDF generation.
"""
import pytest
from backend.graphic_novel_engine import GraphicNovelEngine, PANEL_LAYOUT_PRESETS


def test_layout_presets_present():
    assert len(PANEL_LAYOUT_PRESETS) >= 6
    assert "1_splash" in PANEL_LAYOUT_PRESETS
    assert "2_cinematic" in PANEL_LAYOUT_PRESETS
    assert "4_quadrant" in PANEL_LAYOUT_PRESETS
    assert "6_grid" in PANEL_LAYOUT_PRESETS
    assert "9_classic" in PANEL_LAYOUT_PRESETS
    assert "webtoon_scroll" in PANEL_LAYOUT_PRESETS


def test_paginate_scenes():
    scenes = [
        {"scene_number": i + 1, "heading": f"INT. SCENE {i+1}", "content": f"Action beat {i+1}\nHARRIS\nDon't move."}
        for i in range(8)
    ]
    pages = GraphicNovelEngine.paginate_scenes(scenes, layout_preset="4_quadrant")
    assert len(pages) == 2
    assert len(pages[0]["panels"]) == 4
    assert len(pages[1]["panels"]) == 4
    assert len(pages[0]["panels"][0]["dialogue_balloons"]) > 0


def test_generate_print_pdf():
    scenes = [{"scene_number": 1, "heading": "INT. LAB", "content": "Doctor works."}]
    pages = GraphicNovelEngine.paginate_scenes(scenes, layout_preset="1_splash")
    pdf_bytes = GraphicNovelEngine.generate_print_pdf("Midnight Chronicle", pages)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes[:4] == b"%PDF"
