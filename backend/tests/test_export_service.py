"""
Unit tests for ExportService — PDF Storyboard Presentation & ZIP generation.
"""
import pytest
import io
import zipfile
from export_service import ExportService


SAMPLE_FRAMES = [
    {
        "scene_number": 1,
        "heading": "INT. DETECTIVE OFFICE - NIGHT",
        "description": "Rain lashes against the blinds. Harris lights a Lucky Strike in the half-dark.",
        "image_path": None,
        "intensity_score": 8.8,
        "intensity_type": "Action Peak",
        "moment_summary": "The first match strike illuminates the blood on his knuckles.",
        "shot_type": "Extreme Close-Up",
        "camera_movement": "Slow Push-In",
        "lens": "35mm Anamorphic",
        "lighting": "Hard Side Key, Deep Venetian Shadow",
    },
    {
        "scene_number": 2,
        "heading": "EXT. RAINY ALLEY - CONTINUOUS",
        "description": "Sirens wail in the distance. The black sedan idles by the fire escape.",
        "image_path": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "intensity_score": 6.2,
        "intensity_type": "Emotional Peak",
        "moment_summary": "He watches his own reflection dissolve in the oil puddle.",
        "shot_type": "High Angle Wide Shot",
        "camera_movement": "Crane Down",
        "lens": "24mm",
        "lighting": "Sodium Vapor Backlight",
    }
]


def test_generate_pdf_bytes_returns_valid_pdf():
    pdf_bytes = ExportService.generate_pdf_bytes(
        project_name="Noir Detective Sample",
        frames=SAMPLE_FRAMES,
        script_format="fountain",
        storyboard_style="oscar_prestige"
    )
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    # PDF magic bytes
    assert pdf_bytes.startswith(b"%PDF")


def test_generate_zip_bytes_returns_valid_zip():
    zip_bytes = ExportService.generate_zip_bytes(
        project_name="Noir Detective Sample",
        frames=SAMPLE_FRAMES
    )
    assert isinstance(zip_bytes, bytes)
    assert len(zip_bytes) > 200

    # Inspect zip contents
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        namelist = zf.namelist()
        assert "shot_list.csv" in namelist
        # Frame 2 has a base64 image, so it should be packed
        assert any(name.startswith("frames/scene_02") for name in namelist)


def test_empty_frames_pdf_generation():
    pdf_bytes = ExportService.generate_pdf_bytes(
        project_name="Empty Project",
        frames=[],
        script_format="text",
        storyboard_style="oscar_prestige"
    )
    assert pdf_bytes.startswith(b"%PDF")
