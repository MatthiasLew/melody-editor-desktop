# Technical Overview — Melody Editor Desktop

## Architecture

The application is divided into three main areas:

- `app/main.py` — application startup, main window and screen navigation,
- `app/core/` — data models, file storage, audio and MIDI,
- `app/ui/` — interface screens, QSS styles and the melody grid widget.

## Data models

A melody project is represented by the `Project` class, while a single note is represented by `Note`. A project stores name, tempo, number of bars, pitch range, note list, creation date and save date.

## Data storage

Runtime data is stored locally in the `data/` directory. Projects are serialized to JSON. MIDI import/export works as an additional music data exchange format.

## Audio

Playback preview uses short WAV files generated for individual notes. WAV export renders the whole melody to a single audio file. MP3 export first renders WAV and then converts it through FFmpeg.

## Limitations

MP3/WAV import is not part of this project. These formats do not store note and bar structure, so converting them back to the grid would require a separate audio analysis module.
