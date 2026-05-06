from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _safe_int(value: Any, default: int, minimum: int | None = None, maximum: int | None = None) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError):
        result = default

    if minimum is not None:
        result = max(minimum, result)

    if maximum is not None:
        result = min(maximum, result)

    return result


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized = value.strip().lower()

        if normalized in {"true", "1", "yes", "y", "on"}:
            return True

        if normalized in {"false", "0", "no", "n", "off"}:
            return False

    if value is None:
        return default

    return bool(value)


def _safe_string(value: Any, default: str) -> str:
    if value is None:
        return default

    text = str(value).strip()
    return text if text else default


@dataclass
class Note:
    id: str
    pitch: int
    time: int

    @classmethod
    def create(cls, pitch: int, time: int) -> "Note":
        return cls(
            id=str(uuid4()),
            pitch=_safe_int(pitch, 0, minimum=0),
            time=_safe_int(time, 0, minimum=0),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Note":
        return cls(
            id=_safe_string(data.get("id"), str(uuid4())),
            pitch=_safe_int(data.get("pitch"), 0, minimum=0),
            time=_safe_int(data.get("time"), 0, minimum=0),
        )


@dataclass
class Project:
    name: str = "Untitled Project"
    tempo: int = 120
    bars: int = 8
    pitch_range: str = "c4-c6"
    notes: list[Note] = field(default_factory=list)
    created_at: str = field(default_factory=_now_iso)
    saved_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Project":
        raw_notes = data.get("notes", [])

        if not isinstance(raw_notes, list):
            raw_notes = []

        notes = [
            Note.from_dict(note)
            for note in raw_notes
            if isinstance(note, dict)
        ]

        return cls(
            name=_safe_string(data.get("name"), "Untitled Project"),
            tempo=_safe_int(data.get("tempo"), 120, minimum=40, maximum=240),
            bars=_safe_int(data.get("bars"), 8, minimum=1, maximum=64),
            pitch_range=_safe_string(
                data.get("pitch_range", data.get("pitchRange")),
                "c4-c6",
            ),
            notes=notes,
            created_at=_safe_string(
                data.get("created_at", data.get("createdAt")),
                _now_iso(),
            ),
            saved_at=data.get("saved_at", data.get("savedAt")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "tempo": self.tempo,
            "bars": self.bars,
            "pitch_range": self.pitch_range,
            "notes": [asdict(note) for note in self.notes],
            "created_at": self.created_at,
            "saved_at": self.saved_at,
        }


@dataclass
class AppSettings:
    language: str = "en"
    volume: int = 75
    theme: str = "light"
    default_tempo: int = 120
    high_contrast: bool = False
    large_text: bool = False
    keyboard_shortcuts: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppSettings":
        language = _safe_string(data.get("language"), "en").lower()
        theme = _safe_string(data.get("theme"), "light").lower()

        if language not in {"en", "pl"}:
            language = "en"

        # Compatibility with older saved settings.
        if theme == "dark":
            theme = "black"

        if theme not in {"light", "black"}:
            theme = "light"

        return cls(
            language=language,
            volume=_safe_int(data.get("volume"), 75, minimum=0, maximum=100),
            theme=theme,
            default_tempo=_safe_int(
                data.get("default_tempo", data.get("defaultTempo")),
                120,
                minimum=40,
                maximum=240,
            ),
            high_contrast=_safe_bool(
                data.get("high_contrast", data.get("highContrast")),
                False,
            ),
            large_text=_safe_bool(
                data.get("large_text", data.get("largeText")),
                False,
            ),
            keyboard_shortcuts=_safe_bool(
                data.get("keyboard_shortcuts", data.get("keyboardShortcuts")),
                True,
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)