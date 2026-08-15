"""
Unit tests for AudioScoringEngine & Foley Generator (Enhancement B).
Validates 16-bit stereo WAV generation and preset configurations.
"""
import wave
import io
import pytest
from backend.audio_scoring_engine import AudioScoringEngine, SCORE_PRESETS, FOLEY_PRESETS


def test_score_presets_structure():
    assert len(SCORE_PRESETS) >= 6
    assert "cinematic_epic" in SCORE_PRESETS
    assert "noir_jazz" in SCORE_PRESETS
    assert "synthwave_thriller" in SCORE_PRESETS
    assert "orchestral_drama" in SCORE_PRESETS
    assert "horror_ambient" in SCORE_PRESETS
    assert "action_percussion" in SCORE_PRESETS


def test_generate_score_track_wav():
    wav_bytes = AudioScoringEngine.generate_score_track("cinematic_epic", duration_seconds=1.0)
    assert isinstance(wav_bytes, bytes)
    assert len(wav_bytes) > 1000

    # Parse with standard wave module
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        assert wf.getnchannels() == 2  # Stereo
        assert wf.getsampwidth() == 2  # 16-bit
        assert wf.getframerate() == 44100
        assert wf.getnframes() == 44100


def test_generate_foley_sfx():
    wav_bytes = AudioScoringEngine.generate_foley_sfx("cinematic_boom")
    assert isinstance(wav_bytes, bytes)
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        assert wf.getnchannels() == 2
        assert wf.getnframes() > 1000
