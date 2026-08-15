"""
Storyboard AI — Ambient Cinematic Scoring & Foley SFX Generator (Phase Enhancement B).
Synthesizes procedural genre-matched cinematic background music and foley sound effects
using pure Python mathematical harmonics, stereo panning, and ADSR envelope modulation.
"""
import io
import math
import struct
import wave
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

SAMPLE_RATE = 44100  # 44.1 kHz CD-quality audio

SCORE_PRESETS = {
    "cinematic_epic": {
        "name": "Cinematic Epic",
        "tempo": 90,
        "base_freq": 55.0,  # A1
        "chords": [[55, 82.4, 110], [49, 73.4, 98], [43.6, 65.4, 87.3], [55, 82.4, 110]],
        "description": "Deep sub-bass drone with slow atmospheric orchestral swells.",
    },
    "noir_jazz": {
        "name": "Noir Melancholy",
        "tempo": 70,
        "base_freq": 65.4,  # C2
        "chords": [[65.4, 98.0, 116.5, 155.5], [58.27, 87.3, 103.8, 138.6], [51.9, 77.8, 92.5, 123.5]],
        "description": "Minor 7th dark jazz harmony with subtle warm vinyl warmth.",
    },
    "synthwave_thriller": {
        "name": "Cyberpunk Synthwave",
        "tempo": 115,
        "base_freq": 65.4,
        "chords": [[65.4, 130.8, 196.0], [77.78, 155.5, 233.0], [58.27, 116.5, 174.6]],
        "description": "Pulsing 80s analog synthesizer arpeggio and bass drive.",
    },
    "orchestral_drama": {
        "name": "Warm Orchestral Drama",
        "tempo": 65,
        "base_freq": 110.0,
        "chords": [[110, 138.6, 164.8, 220], [98, 123.5, 146.8, 196], [87.3, 110, 130.8, 174.6]],
        "description": "Lush string ensemble pads with emotional harmonic movement.",
    },
    "horror_ambient": {
        "name": "Horror & Suspense Drone",
        "tempo": 50,
        "base_freq": 43.6,  # F1
        "chords": [[43.6, 46.25, 61.7], [41.2, 43.6, 58.2]],
        "description": "Dissonant low-frequency cluster drone and eerie high harmonic glimmers.",
    },
    "action_percussion": {
        "name": "Tactical Action Pulse",
        "tempo": 130,
        "base_freq": 60.0,
        "chords": [[60, 90, 120], [60, 80, 120]],
        "description": "Rhythmic cinematic drum pulse with filtered bass transients.",
    },
}

FOLEY_PRESETS = {
    "rain_storm": {"name": "Thunderstorm & Rain Ambience", "type": "noise", "duration": 4.0},
    "gunshot_reverb": {"name": "Pistol Shot with Tail Echo", "type": "impulse", "duration": 2.0},
    "footsteps_corridor": {"name": "Paced Leather Footsteps", "type": "footsteps", "duration": 3.0},
    "door_creak": {"name": "Heavy Iron Door Creak", "type": "creak", "duration": 2.5},
    "cinematic_boom": {"name": "Sub-Bass Cinematic Hit (Braam)", "type": "braam", "duration": 3.0},
}


class AudioScoringEngine:
    """Procedural audio synthesis engine for cinematic scores and foley sound effects."""

    @staticmethod
    def generate_score_track(preset_key: str = "cinematic_epic", duration_seconds: float = 12.0) -> bytes:
        """
        Synthesizes a stereo 44.1kHz WAV background score track.
        """
        preset = SCORE_PRESETS.get(preset_key, SCORE_PRESETS["cinematic_epic"])
        total_samples = int(SAMPLE_RATE * duration_seconds)
        chord_list = preset["chords"]
        chord_duration = duration_seconds / len(chord_list)

        buf = io.BytesIO()
        with wave.open(buf, "wb") as wav_file:
            wav_file.setnchannels(2)  # Stereo
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(SAMPLE_RATE)

            frames = bytearray()
            for i in range(total_samples):
                t = i / SAMPLE_RATE
                chord_idx = min(len(chord_list) - 1, int(t / chord_duration))
                active_chord = chord_list[chord_idx]

                # Synthesize harmonic tones
                left_sample = 0.0
                right_sample = 0.0

                for f_idx, freq in enumerate(active_chord):
                    # Fundamental + Warm 2nd harmonic
                    wave_val = (
                        math.sin(2.0 * math.pi * freq * t) * 0.5 +
                        math.sin(2.0 * math.pi * (freq * 2.0) * t) * 0.25 +
                        math.sin(2.0 * math.pi * (freq * 3.0) * t) * 0.1
                    )
                    # Pan frequencies across stereo field
                    pan = (f_idx / max(1, len(active_chord) - 1))
                    left_sample += wave_val * (1.0 - pan * 0.5)
                    right_sample += wave_val * (0.5 + pan * 0.5)

                # Add gentle breathing tremolo
                lfo = 0.85 + 0.15 * math.sin(2.0 * math.pi * 0.5 * t)
                left_sample *= lfo
                right_sample *= lfo

                # Master fade in / out envelope
                fade_len = min(1.5, duration_seconds * 0.2)
                env = 1.0
                if t < fade_len:
                    env = t / fade_len
                elif t > (duration_seconds - fade_len):
                    env = (duration_seconds - t) / fade_len
                env = max(0.0, min(1.0, env))

                # Normalize & pack into 16-bit PCM (-32768 to 32767)
                l_int = int(max(-1.0, min(1.0, (left_sample / len(active_chord)) * env * 0.7)) * 32760)
                r_int = int(max(-1.0, min(1.0, (right_sample / len(active_chord)) * env * 0.7)) * 32760)

                frames.extend(struct.pack("<hh", l_int, r_int))

            wav_file.writeframes(frames)

        return buf.getvalue()

    @staticmethod
    def generate_foley_sfx(sfx_key: str = "cinematic_boom") -> bytes:
        """
        Synthesizes a short foley sound effect (WAV).
        """
        preset = FOLEY_PRESETS.get(sfx_key, FOLEY_PRESETS["cinematic_boom"])
        duration = preset.get("duration", 2.5)
        total_samples = int(SAMPLE_RATE * duration)

        buf = io.BytesIO()
        with wave.open(buf, "wb") as wav_file:
            wav_file.setnchannels(2)
            wav_file.setsampwidth(2)
            wav_file.setframerate(SAMPLE_RATE)

            frames = bytearray()
            for i in range(total_samples):
                t = i / SAMPLE_RATE
                val = 0.0

                if preset["type"] == "braam":
                    # Pitch-drop sub-bass hit
                    freq = 80.0 * math.exp(-t * 2.0) + 35.0
                    val = math.sin(2.0 * math.pi * freq * t) * math.exp(-t * 1.5)
                    # Add brass distortion overtone
                    val += math.sin(2.0 * math.pi * freq * 2.5 * t) * 0.3 * math.exp(-t * 3.0)
                elif preset["type"] == "impulse":
                    # Gunshot impulse & reverb
                    if t < 0.05:
                        val = ((i % 100) / 50.0 - 1.0)
                    else:
                        val = ((i % 80) / 40.0 - 1.0) * math.exp(-t * 4.0) * 0.4
                elif preset["type"] == "footsteps":
                    # Periodic step impact
                    step_phase = (t * 2.0) % 1.0
                    if step_phase < 0.1:
                        val = math.sin(2.0 * math.pi * 90.0 * step_phase) * (1.0 - step_phase * 10)
                else:
                    # Filtered noise / creak
                    val = (math.sin(2.0 * math.pi * 120.0 * t) + math.sin(2.0 * math.pi * 340.0 * t)) * math.exp(-t * 0.8)

                s_int = int(max(-1.0, min(1.0, val * 0.8)) * 32760)
                frames.extend(struct.pack("<hh", s_int, s_int))

            wav_file.writeframes(frames)

        return buf.getvalue()
