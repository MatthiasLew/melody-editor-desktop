from __future__ import annotations

import math
import struct
import tempfile
import wave
from pathlib import Path

from PySide6.QtCore import QObject, QUrl
from PySide6.QtMultimedia import QSoundEffect


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


class AudioEngine(QObject):
    """
    Simple audio engine for Melody Editor.

    It generates short WAV files for musical notes and plays them using QSoundEffect.
    This keeps the prototype independent from external audio libraries.
    """

    SAMPLE_RATE = 44_100
    DURATION_SECONDS = 0.22
    MAX_AMPLITUDE = 28_000

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self.cache_dir = Path(tempfile.gettempdir()) / "melody_editor_sounds"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.effects: dict[str, QSoundEffect] = {}

    def play_note(self, note_name: str, volume: int = 75) -> None:
        """
        Play one note, for example C4, D5, A4.
        """

        normalized_note = note_name.strip().upper()

        if normalized_note not in self.effects:
            wav_path = self._ensure_note_file(normalized_note)

            effect = QSoundEffect(self)
            effect.setSource(QUrl.fromLocalFile(str(wav_path)))
            effect.setLoopCount(1)

            self.effects[normalized_note] = effect

        effect = self.effects[normalized_note]
        effect.stop()
        effect.setVolume(self._normalize_volume(volume))
        effect.play()

    def play_notes(self, note_names: list[str], volume: int = 75) -> None:
        """
        Play multiple notes at the same timeline step.
        """

        for note_name in note_names:
            self.play_note(note_name, volume)

    def _ensure_note_file(self, note_name: str) -> Path:
        wav_path = self.cache_dir / f"{note_name}.wav"

        if wav_path.exists():
            return wav_path

        frequency = self._note_to_frequency(note_name)
        self._write_sine_wave(wav_path, frequency)

        return wav_path

    def _write_sine_wave(self, path: Path, frequency: float) -> None:
        total_samples = int(self.SAMPLE_RATE * self.DURATION_SECONDS)
        fade_samples = int(self.SAMPLE_RATE * 0.015)

        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.SAMPLE_RATE)

            for sample_index in range(total_samples):
                time = sample_index / self.SAMPLE_RATE
                raw_value = math.sin(2 * math.pi * frequency * time)

                envelope = 1.0

                if sample_index < fade_samples:
                    envelope = sample_index / fade_samples
                elif sample_index > total_samples - fade_samples:
                    envelope = (total_samples - sample_index) / fade_samples

                value = int(self.MAX_AMPLITUDE * raw_value * envelope)
                wav_file.writeframes(struct.pack("<h", value))

    @staticmethod
    def _note_to_frequency(note_name: str) -> float:
        note = note_name[:-1]
        octave_text = note_name[-1]

        if note not in NOTE_TO_SEMITONE or not octave_text.isdigit():
            raise ValueError(f"Unsupported note name: {note_name}")

        octave = int(octave_text)

        midi_number = (octave + 1) * 12 + NOTE_TO_SEMITONE[note]
        return 440.0 * (2 ** ((midi_number - 69) / 12))

    @staticmethod
    def _normalize_volume(volume: int) -> float:
        return max(0.0, min(1.0, volume / 100))