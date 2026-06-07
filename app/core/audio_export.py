from __future__ import annotations

import math
import shutil
import struct
import subprocess
import tempfile
import wave
from pathlib import Path

from app.core.models import Project

SAMPLE_RATE = 44_100
MAX_AMPLITUDE = 26_000

PITCH_RANGES = {
    "c3-c5": [
        "C5", "B4", "A4", "G4", "F4",
        "E4", "D4", "C4", "B3", "A3",
        "G3", "F3", "E3", "D3", "C3",
    ],
    "c4-c6": [
        "C6", "B5", "A5", "G5", "F5",
        "E5", "D5", "C5", "B4", "A4",
        "G4", "F4", "E4", "D4", "C4",
    ],
    "c5-c7": [
        "C7", "B6", "A6", "G6", "F6",
        "E6", "D6", "C6", "B5", "A5",
        "G5", "F5", "E5", "D5", "C5",
    ],
}

NOTE_TO_SEMITONE = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11,
}


def export_project_to_audio(project: Project, target_path: str | Path) -> None:
    path = Path(target_path)
    suffix = path.suffix.lower()

    if suffix in {"", ".wav"}:
        if suffix == "":
            path = path.with_suffix(".wav")
        export_project_to_wav(project, path)
        return

    if suffix == ".mp3":
        export_project_to_mp3(project, path)
        return

    raise ValueError("Unsupported audio format. Use WAV or MP3.")


def export_project_to_wav(project: Project, target_path: str | Path) -> None:
    path = Path(target_path)
    if path.suffix.lower() != ".wav":
        path = path.with_suffix(".wav")

    samples = _render_project_samples(project)

    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)

        for sample in samples:
            wav_file.writeframes(struct.pack("<h", int(max(-32767, min(32767, sample)))))


def export_project_to_mp3(project: Project, target_path: str | Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise ValueError("FFmpeg not found in PATH")

    path = Path(target_path)
    if path.suffix.lower() != ".mp3":
        path = path.with_suffix(".mp3")

    path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="melody_editor_export_") as temporary_dir:
        wav_path = Path(temporary_dir) / "melody_export.wav"
        export_project_to_wav(project, wav_path)

        completed = subprocess.run(
            [
                ffmpeg,
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(wav_path),
                str(path),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        if completed.returncode != 0:
            message = completed.stderr.strip() or "FFmpeg failed to create MP3 file."
            raise ValueError(message)


def _render_project_samples(project: Project) -> list[int]:
    tempo = max(1, int(project.tempo))
    step_seconds = 60.0 / tempo
    note_duration_seconds = max(0.08, step_seconds * 0.9)

    last_note_step = max((note.time for note in project.notes), default=max(0, project.bars * 4 - 1))
    total_seconds = (last_note_step + 1) * step_seconds + 0.25
    total_samples = max(1, int(total_seconds * SAMPLE_RATE))
    samples = [0.0] * total_samples

    pitch_names = PITCH_RANGES.get(project.pitch_range, PITCH_RANGES["c4-c6"])

    for note in project.notes:
        if not (0 <= note.pitch < len(pitch_names)):
            continue

        frequency = _note_to_frequency(pitch_names[note.pitch])
        start_sample = int(max(0, note.time) * step_seconds * SAMPLE_RATE)
        note_samples = int(note_duration_seconds * SAMPLE_RATE)
        fade_samples = max(1, int(SAMPLE_RATE * 0.015))

        for index in range(note_samples):
            target_index = start_sample + index
            if target_index >= total_samples:
                break

            time = index / SAMPLE_RATE
            envelope = 1.0

            if index < fade_samples:
                envelope = index / fade_samples
            elif index > note_samples - fade_samples:
                envelope = max(0.0, (note_samples - index) / fade_samples)

            samples[target_index] += math.sin(2 * math.pi * frequency * time) * envelope

    peak = max((abs(value) for value in samples), default=1.0)
    if peak <= 0:
        return [0 for _ in samples]

    scale = MAX_AMPLITUDE / peak
    return [int(value * scale) for value in samples]


def _note_to_frequency(note_name: str) -> float:
    normalized = note_name.strip().upper()
    note = normalized[:-1]
    octave_text = normalized[-1]

    if note not in NOTE_TO_SEMITONE or not octave_text.isdigit():
        raise ValueError(f"Unsupported note name: {note_name}")

    octave = int(octave_text)
    midi_number = (octave + 1) * 12 + NOTE_TO_SEMITONE[note]
    return 440.0 * (2 ** ((midi_number - 69) / 12))
