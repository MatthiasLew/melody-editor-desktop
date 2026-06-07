# Melody Editor Desktop

[Polska wersja](README.pl.md)

Melody Editor Desktop is a simple desktop application for creating short melodies on a grid-based musical editor. The vertical axis represents pitch, the horizontal axis represents time, and playback is shown with a moving timeline line.

The project was created as a human-computer interaction/user interface laboratory project. It focuses on clear navigation, simple editing, local project storage and basic import/export support.

## Features

- Create a new melody project.
- Add notes by clicking on the editor grid.
- Move selected notes with keyboard shortcuts.
- Delete notes with the Delete key or right mouse button.
- Play and stop the melody preview.
- Start playback from a selected position.
- Loop playback after the last note.
- Save projects locally.
- Import and export project files as JSON and MIDI.
- Export audio as WAV.
- Export audio as MP3 when FFmpeg is available in the system PATH.
- Switch between Polish and English interface language.
- Use light, black and high-contrast display modes.

## Technologies

- Python 3.11+
- PySide6
- JSON for local project storage
- Standard Python libraries for WAV rendering
- MIDI import/export implemented directly in Python
- FFmpeg for optional MP3 export

## Project structure

```text
melody-editor-desktop/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── audio.py
│   │   ├── audio_export.py
│   │   ├── midi.py
│   │   ├── models.py
│   │   └── storage.py
│   └── ui/
│       ├── styles.py
│       ├── widgets.py
│       └── screens/
│           ├── base.py
│           ├── editor_screen.py
│           ├── help_screen.py
│           ├── load_project_screen.py
│           ├── new_project_screen.py
│           ├── save_project_screen.py
│           ├── settings_screen.py
│           └── start_screen.py
├── data/
├── run.py
├── requirements.txt
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/MatthiasLew/melody-editor-desktop.git
cd melody-editor-desktop
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
.venv\Scripts\activate.bat
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the application

```bash
python run.py
```

Alternative module-style command:

```bash
python -m app.main
```

## File formats

| Format | Direction | Purpose | Notes |
|---|---|---|---|
| JSON | import/export | Editable project file | Recommended for saving full project data. |
| MIDI | import/export | Musical note exchange | Useful for moving melodies between music tools. |
| WAV | export only | Audio output | Works without additional external tools. |
| MP3 | export only | Compressed audio output | Requires FFmpeg installed and available in PATH. |

MP3 and WAV import is intentionally not supported. These formats contain final audio, not structured editable project data. Converting an audio recording back into editable notes would require pitch and rhythm detection, which is outside the scope of this project.

## FFmpeg for MP3 export

MP3 export requires FFmpeg. If FFmpeg is not installed, use WAV export instead.

To check whether FFmpeg is available:

```bash
ffmpeg -version
```

If the command is not recognized, install FFmpeg and add it to the system PATH, then restart the application.

## Basic usage

1. Open the application.
2. Choose **New Project**.
3. Set project name, tempo, number of bars and pitch range.
4. Click cells on the grid to add notes.
5. Select a note and use arrow keys to move it.
6. Press Delete or right-click a note to remove it.
7. Use Play/Stop to preview the melody.
8. Save the project or export it to JSON, MIDI, WAV or MP3.

## Runtime data

The application stores local runtime data in the `data/` directory. User-generated JSON files in this directory should not be committed to the repository.

## Development notes

Recommended local checks before committing:

```bash
python -m compileall app
python run.py
```

