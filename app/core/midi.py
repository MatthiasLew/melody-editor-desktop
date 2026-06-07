from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from app.core.models import Note, Project

TICKS_PER_BEAT = 480
STEPS_PER_BAR = 4

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

SEMITONE_TO_NOTE = {
    0: "C",
    1: "C#",
    2: "D",
    3: "D#",
    4: "E",
    5: "F",
    6: "F#",
    7: "G",
    8: "G#",
    9: "A",
    10: "A#",
    11: "B",
}


@dataclass(frozen=True)
class MidiNoteEvent:
    start_tick: int
    note_number: int
    velocity: int = 90


def note_name_to_midi(note_name: str) -> int:
    normalized = note_name.strip().upper()
    note = normalized[:-1]
    octave_text = normalized[-1]

    if note not in NOTE_TO_SEMITONE or not octave_text.isdigit():
        raise ValueError(f"Unsupported note name: {note_name}")

    octave = int(octave_text)
    return (octave + 1) * 12 + NOTE_TO_SEMITONE[note]


def midi_to_note_name(note_number: int) -> str:
    octave = note_number // 12 - 1
    note = SEMITONE_TO_NOTE[note_number % 12]
    return f"{note}{octave}"


def export_project_to_midi(project: Project, target_path: str | Path) -> None:
    path = Path(target_path)
    if path.suffix.lower() not in {".mid", ".midi"}:
        path = path.with_suffix(".mid")

    pitch_names = PITCH_RANGES.get(project.pitch_range, PITCH_RANGES["c4-c6"])
    events: list[tuple[int, int, bytes]] = []

    # Meta tempo event at the beginning of the track.
    microseconds_per_beat = int(60_000_000 / max(1, min(300, project.tempo)))
    events.append((0, 0, b"\xff\x51\x03" + microseconds_per_beat.to_bytes(3, "big")))

    for note in project.notes:
        if not (0 <= note.pitch < len(pitch_names)):
            continue

        midi_number = note_name_to_midi(pitch_names[note.pitch])
        start_tick = max(0, int(note.time)) * TICKS_PER_BEAT
        end_tick = start_tick + int(TICKS_PER_BEAT * 0.9)

        events.append((start_tick, 1, bytes([0x90, midi_number, 90])))
        events.append((end_tick, 0, bytes([0x80, midi_number, 0])))

    events.sort(key=lambda item: (item[0], item[1]))

    track_data = bytearray()
    previous_tick = 0

    for tick, _, payload in events:
        delta = max(0, tick - previous_tick)
        track_data.extend(_write_variable_length_quantity(delta))
        track_data.extend(payload)
        previous_tick = tick

    track_data.extend(_write_variable_length_quantity(0))
    track_data.extend(b"\xff\x2f\x00")

    header = b"MThd" + (6).to_bytes(4, "big")
    header += (0).to_bytes(2, "big")  # format 0
    header += (1).to_bytes(2, "big")  # one track
    header += TICKS_PER_BEAT.to_bytes(2, "big")

    track = b"MTrk" + len(track_data).to_bytes(4, "big") + bytes(track_data)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(header + track)


def import_project_from_midi(source_path: str | Path) -> Project:
    path = Path(source_path)
    data = path.read_bytes()
    tracks, division = _parse_midi_file(data)

    all_note_events: list[MidiNoteEvent] = []
    tempo = 120

    for track in tracks:
        note_events, track_tempo = _parse_track_events(track)
        all_note_events.extend(note_events)

        if track_tempo is not None:
            tempo = track_tempo

    if division <= 0:
        division = TICKS_PER_BEAT

    pitch_range = _choose_pitch_range(event.note_number for event in all_note_events)
    pitch_names = PITCH_RANGES[pitch_range]
    midi_to_pitch = {note_name_to_midi(name): index for index, name in enumerate(pitch_names)}

    notes: list[Note] = []
    occupied_cells: set[tuple[int, int]] = set()

    for event in sorted(all_note_events, key=lambda item: item.start_tick):
        nearest_midi = min(midi_to_pitch, key=lambda item: abs(item - event.note_number))
        pitch = midi_to_pitch[nearest_midi]
        step = round(event.start_tick / division)
        cell = (pitch, step)

        if cell in occupied_cells:
            continue

        occupied_cells.add(cell)
        notes.append(Note.create(pitch=pitch, time=step))

    max_step = max((note.time for note in notes), default=31)
    bars = max(1, min(64, (max_step // STEPS_PER_BAR) + 1))

    return Project(
        name=path.stem or "Imported MIDI",
        tempo=tempo,
        bars=bars,
        pitch_range=pitch_range,
        notes=notes,
    )


def _choose_pitch_range(note_numbers: Iterable[int]) -> str:
    values = list(note_numbers)
    if not values:
        return "c4-c6"

    minimum = min(values)
    maximum = max(values)

    for range_name, pitch_names in PITCH_RANGES.items():
        midi_values = [note_name_to_midi(name) for name in pitch_names]
        if min(midi_values) <= minimum and maximum <= max(midi_values):
            return range_name

    # Prefer the range whose center is closest to the imported melody.
    melody_center = (minimum + maximum) / 2
    return min(
        PITCH_RANGES,
        key=lambda range_name: abs(
            melody_center
            - sum(note_name_to_midi(name) for name in PITCH_RANGES[range_name])
            / len(PITCH_RANGES[range_name])
        ),
    )


def _parse_midi_file(data: bytes) -> tuple[list[bytes], int]:
    if len(data) < 14 or data[:4] != b"MThd":
        raise ValueError("Selected file is not a valid MIDI file.")

    header_length = int.from_bytes(data[4:8], "big")
    if header_length < 6:
        raise ValueError("Invalid MIDI header length.")

    header_start = 8
    header_end = header_start + header_length
    if len(data) < header_end:
        raise ValueError("MIDI file is truncated.")

    track_count = int.from_bytes(data[10:12], "big")
    division = int.from_bytes(data[12:14], "big", signed=False)

    tracks: list[bytes] = []
    offset = header_end

    for _ in range(track_count):
        if offset + 8 > len(data) or data[offset:offset + 4] != b"MTrk":
            raise ValueError("MIDI track header is missing or damaged.")

        track_length = int.from_bytes(data[offset + 4:offset + 8], "big")
        track_start = offset + 8
        track_end = track_start + track_length

        if track_end > len(data):
            raise ValueError("MIDI track data is truncated.")

        tracks.append(data[track_start:track_end])
        offset = track_end

    return tracks, division


def _parse_track_events(track: bytes) -> tuple[list[MidiNoteEvent], int | None]:
    events: list[MidiNoteEvent] = []
    active_notes: dict[tuple[int, int], int] = {}
    tempo: int | None = None

    absolute_tick = 0
    offset = 0
    running_status: int | None = None

    while offset < len(track):
        delta, offset = _read_variable_length_quantity(track, offset)
        absolute_tick += delta

        if offset >= len(track):
            break

        status = track[offset]

        if status < 0x80:
            if running_status is None:
                raise ValueError("Invalid MIDI running status.")
            status = running_status
        else:
            offset += 1
            if status < 0xF0:
                running_status = status

        if status == 0xFF:
            if offset >= len(track):
                break
            meta_type = track[offset]
            offset += 1
            length, offset = _read_variable_length_quantity(track, offset)
            payload = track[offset:offset + length]
            offset += length

            if meta_type == 0x51 and len(payload) == 3:
                microseconds_per_beat = int.from_bytes(payload, "big")
                if microseconds_per_beat > 0:
                    tempo = round(60_000_000 / microseconds_per_beat)

            if meta_type == 0x2F:
                break

            continue

        if status in {0xF0, 0xF7}:
            length, offset = _read_variable_length_quantity(track, offset)
            offset += length
            continue

        event_type = status & 0xF0
        channel = status & 0x0F

        if event_type in {0x80, 0x90, 0xA0, 0xB0, 0xE0}:
            if offset + 2 > len(track):
                break
            first = track[offset]
            second = track[offset + 1]
            offset += 2

            if event_type == 0x90 and second > 0:
                active_notes[(channel, first)] = absolute_tick
            elif event_type == 0x80 or (event_type == 0x90 and second == 0):
                start_tick = active_notes.pop((channel, first), absolute_tick)
                events.append(MidiNoteEvent(start_tick=start_tick, note_number=first, velocity=second))

            continue

        if event_type in {0xC0, 0xD0}:
            offset += 1
            continue

        raise ValueError(f"Unsupported MIDI event: 0x{status:02X}")

    for (_, note_number), start_tick in active_notes.items():
        events.append(MidiNoteEvent(start_tick=start_tick, note_number=note_number))

    return events, tempo


def _read_variable_length_quantity(data: bytes, offset: int) -> tuple[int, int]:
    value = 0

    for _ in range(4):
        if offset >= len(data):
            raise ValueError("Unexpected end of variable length quantity.")

        byte = data[offset]
        offset += 1
        value = (value << 7) | (byte & 0x7F)

        if not byte & 0x80:
            return value, offset

    raise ValueError("Invalid variable length quantity.")


def _write_variable_length_quantity(value: int) -> bytes:
    value = max(0, int(value))
    buffer = value & 0x7F
    output = bytearray()

    while value >> 7:
        value >>= 7
        buffer <<= 8
        buffer |= (value & 0x7F) | 0x80

    while True:
        output.append(buffer & 0xFF)
        if buffer & 0x80:
            buffer >>= 8
        else:
            break

    return bytes(output)
