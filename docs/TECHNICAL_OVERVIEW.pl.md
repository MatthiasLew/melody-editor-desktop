# Opis techniczny — Melody Editor Desktop

## Architektura

Aplikacja jest podzielona na trzy główne obszary:

- `app/main.py` — start aplikacji, główne okno i przełączanie ekranów,
- `app/core/` — modele danych, zapis plików, audio, MIDI,
- `app/ui/` — ekrany interfejsu, style QSS i widget siatki melodii.

## Modele danych

Projekt melodii jest reprezentowany przez klasę `Project`, a pojedyncza nuta przez `Note`. Projekt przechowuje nazwę, tempo, liczbę taktów, zakres dźwięków, listę nut oraz daty utworzenia i zapisu.

## Zapis danych

Dane robocze są zapisywane lokalnie w katalogu `data/`. Projekty są serializowane do JSON. Import/eksport MIDI działa jako dodatkowy format wymiany danych muzycznych.

## Audio

Podgląd dźwięku w aplikacji wykorzystuje krótkie pliki WAV generowane dla konkretnych nut. Eksport WAV renderuje całą melodię do jednego pliku audio. Eksport MP3 wykonuje najpierw render WAV, a następnie konwersję przez FFmpeg.

## Ograniczenia

Import MP3/WAV nie jest częścią projektu. Te formaty nie przechowują struktury nut i taktów, dlatego ich konwersja do siatki wymagałaby osobnego modułu analizy audio.
