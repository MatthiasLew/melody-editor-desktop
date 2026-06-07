# Melody Editor Desktop

[English version](README.md)

Melody Editor Desktop to prosta aplikacja desktopowa do tworzenia krótkich melodii na siatce muzycznej. Oś pionowa odpowiada za wysokość dźwięku, oś pozioma za czas, a odtwarzanie jest pokazane za pomocą przesuwającej się linii czasu.

Projekt powstał jako aplikacja do laboratorium z komunikacji człowiek-komputer/projektowania interfejsu użytkownika. Główny nacisk położono na czytelną nawigację, prostą edycję, lokalny zapis projektów oraz podstawowy import i eksport plików.

## Funkcje

- Tworzenie nowego projektu melodii.
- Dodawanie nut przez kliknięcie na siatce edytora.
- Przesuwanie zaznaczonych nut skrótami klawiaturowymi.
- Usuwanie nut klawiszem Delete albo prawym przyciskiem myszy.
- Odtwarzanie i zatrzymywanie podglądu melodii.
- Rozpoczynanie odtwarzania od wybranej pozycji.
- Zapętlanie odtwarzania po ostatniej nucie.
- Lokalny zapis projektów.
- Import i eksport projektów w formacie JSON oraz MIDI.
- Eksport audio do WAV.
- Eksport audio do MP3, jeżeli FFmpeg jest dostępny w zmiennej PATH.
- Zmiana języka interfejsu: polski/angielski.
- Motyw jasny, czarny oraz tryb wysokiego kontrastu.

## Technologie

- Python 3.11+
- PySide6
- JSON do lokalnego zapisu projektów
- Standardowe biblioteki Pythona do generowania WAV
- Import/eksport MIDI zaimplementowany bezpośrednio w Pythonie
- FFmpeg do opcjonalnego eksportu MP3

## Struktura projektu

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

## Instalacja

Sklonuj repozytorium:

```bash
git clone https://github.com/MatthiasLew/melody-editor-desktop.git
cd melody-editor-desktop
```

Utwórz i aktywuj środowisko wirtualne:

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

Zainstaluj zależności:

```bash
pip install -r requirements.txt
```

## Uruchomienie aplikacji

```bash
python run.py
```

Alternatywnie:

```bash
python -m app.main
```

## Format plików

| Format | Kierunek | Zastosowanie | Uwagi |
|---|---|---|---|
| JSON | import/eksport | Edytowalny plik projektu | Zalecany do zapisywania pełnych danych projektu. |
| MIDI | import/eksport | Wymiana danych muzycznych | Przydatny do przenoszenia melodii między narzędziami muzycznymi. |
| WAV | tylko eksport | Gotowy plik audio | Działa bez dodatkowych narzędzi zewnętrznych. |
| MP3 | tylko eksport | Skompresowany plik audio | Wymaga zainstalowanego FFmpeg dostępnego w PATH. |

Import MP3 i WAV nie jest obsługiwany celowo. Te formaty przechowują gotowe audio, a nie uporządkowane dane projektu. Zamiana nagrania audio z powrotem na edytowalne nuty wymagałaby wykrywania wysokości dźwięku i rytmu, co wykracza poza zakres tego projektu.

## FFmpeg do eksportu MP3

Eksport MP3 wymaga programu FFmpeg. Jeżeli FFmpeg nie jest zainstalowany, należy użyć eksportu WAV.

Sprawdzenie dostępności FFmpeg:

```bash
ffmpeg -version
```

Jeżeli polecenie nie jest rozpoznawane, należy zainstalować FFmpeg, dodać go do zmiennej PATH i ponownie uruchomić aplikację.

## Podstawowa obsługa

1. Uruchom aplikację.
2. Wybierz **Nowy projekt**.
3. Ustaw nazwę projektu, tempo, liczbę taktów i zakres dźwięków.
4. Klikaj pola na siatce, aby dodawać nuty.
5. Zaznacz nutę i użyj strzałek, aby ją przesunąć.
6. Naciśnij Delete albo kliknij nutę prawym przyciskiem myszy, aby ją usunąć.
7. Użyj Play/Stop, aby odsłuchać melodię.
8. Zapisz projekt albo wyeksportuj go do JSON, MIDI, WAV lub MP3.

## Dane robocze

Aplikacja zapisuje dane robocze w katalogu `data/`. Pliki JSON tworzone lokalnie w tym katalogu nie powinny być dodawane do repozytorium.

## Uwagi developerskie

Zalecane sprawdzenia przed commitem:

```bash
python -m compileall app
python run.py
```

