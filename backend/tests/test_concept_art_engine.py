"""
Unit tests for ConceptArtEngine (Phase 8).
Validates prompt builders, model sheets, and look-book PDF generation.
"""
import pytest
from backend.concept_art_engine import ConceptArtEngine


def test_build_portrait_prompt():
    char = {
        "name": "MARCUS VANCE",
        "role": "Noir Detective",
        "description": "Weathered 40s detective with sharp jawline and cynical eyes.",
        "wardrobe": "Charcoal trenchcoat and fedora",
    }
    prompt = ConceptArtEngine.build_portrait_prompt(char, style_prefix="Cinematic 35mm film.")
    assert "MARCUS VANCE" in prompt
    assert "Noir Detective" in prompt
    assert "Charcoal trenchcoat" in prompt
    assert "Cinematic 35mm film." in prompt


def test_build_expression_matrix_prompt():
    char = {"name": "ELENA", "description": "Cyberpunk hacker"}
    prompt = ConceptArtEngine.build_expression_matrix_prompt(char)
    assert "ELENA" in prompt
    assert "6 distinct facial expressions" in prompt


def test_build_turnaround_prompt():
    char = {"name": "KAI", "description": "Space pilot", "wardrobe": "Flight suit"}
    prompt = ConceptArtEngine.build_turnaround_prompt(char)
    assert "KAI" in prompt
    assert "4 distinct full-body views" in prompt


def test_generate_lookbook_pdf():
    characters = [
        {
            "name": "MARCUS VANCE",
            "role": "Detective",
            "description": "Cynical detective.",
            "wardrobe": "Trenchcoat",
            "voice_id": "onyx",
            "is_lead": True,
            "visual_prompt": "Marcus Vance in a trenchcoat",
        }
    ]
    pdf_bytes = ConceptArtEngine.generate_lookbook_pdf("Neon Rain", characters)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes[:4] == b"%PDF"
