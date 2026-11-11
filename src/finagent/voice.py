"""Stage 2 (owner: B). Fill audio_path and duration_s for every scene.

MOCK: no audio, duration estimated at ~15 characters per second. Replace the body
with real TTS (and avatar, if any); keep the signature.
"""
from pathlib import Path

from contracts.schemas import Presentation


def synthesize(presentation: Presentation, out_dir: Path) -> Presentation:
    result = presentation.model_copy(deep=True)
    for scene in result.scenes:
        scene.audio_path = None
        scene.duration_s = round(max(2.0, len(scene.narration) / 15), 1)
    return result
