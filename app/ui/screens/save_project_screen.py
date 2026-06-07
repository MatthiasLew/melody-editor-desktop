from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QVBoxLayout,
)

from app.core.models import Project
from app.ui.screens.base import BaseScreen

if TYPE_CHECKING:
    from app.main import MainWindow


TEXTS = {
    "en": {
        "back": "←  Back to Editor",
        "title": "Save Project",
        "subtitle": "Save your melody project or export it to common file formats",
        "file_name": "File Name",
        "file_placeholder": "Enter project file name",
        "save_location": "Save Location",
        "location": "💾  Local project library / JSON",
        "recent_files": "Recent Files",
        "no_recent": "No recent files",
        "cancel": "Cancel",
        "save": "Save Project",
        "message_title": "Save Project",
        "no_project": "There is no active project to save.",
        "empty_name": "File name cannot be empty.",
        "saved": "Project saved locally.",
        "export_project": "📤  Export Project...",
        "export_audio": "🎧  Export Audio...",
        "project_exported": "Project exported successfully.",
        "audio_exported": "Audio exported successfully.",
        "export_error": "Could not export file.",
        "project_filter": "Project files (*.json *.mid *.midi);;JSON files (*.json);;MIDI files (*.mid *.midi)",
        "audio_filter": "WAV audio (*.wav);;MP3 audio (*.mp3)",
        "mp3_ffmpeg_missing": "MP3 export requires FFmpeg. FFmpeg was not found in PATH. Export to WAV or install FFmpeg and restart the app.",
    },
    "pl": {
        "back": "←  Powrót do edytora",
        "title": "Zapisz projekt",
        "subtitle": "Zapisz projekt melodii albo wyeksportuj go do popularnych formatów",
        "file_name": "Nazwa pliku",
        "file_placeholder": "Wpisz nazwę projektu",
        "save_location": "Miejsce zapisu",
        "location": "💾  Lokalna biblioteka projektów / JSON",
        "recent_files": "Ostatnie pliki",
        "no_recent": "Brak ostatnich plików",
        "cancel": "Anuluj",
        "save": "Zapisz projekt",
        "message_title": "Zapis projektu",
        "no_project": "Brak aktywnego projektu do zapisania.",
        "empty_name": "Nazwa pliku nie może być pusta.",
        "saved": "Projekt został zapisany lokalnie.",
        "export_project": "📤  Eksportuj projekt...",
        "export_audio": "🎧  Eksportuj audio...",
        "project_exported": "Projekt został wyeksportowany.",
        "audio_exported": "Audio zostało wyeksportowane.",
        "export_error": "Nie udało się wyeksportować pliku.",
        "project_filter": "Pliki projektu (*.json *.mid *.midi);;Pliki JSON (*.json);;Pliki MIDI (*.mid *.midi)",
        "audio_filter": "Audio WAV (*.wav);;Audio MP3 (*.mp3)",
        "mp3_ffmpeg_missing": "Eksport MP3 wymaga programu FFmpeg. Nie znaleziono FFmpeg w zmiennej PATH. Wyeksportuj WAV albo zainstaluj FFmpeg i uruchom aplikację ponownie.",
    },
}


class SaveProjectScreen(BaseScreen):
    """Screen used to save and export the current project."""

    def __init__(self, controller: "MainWindow") -> None:
        super().__init__(controller)

        card = self.make_card(max_width=820)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(42, 36, 42, 36)
        layout.setSpacing(18)

        self.back_button = self.normal_button("")
        self.back_button.setMaximumWidth(210)
        self.back_button.clicked.connect(lambda: self.controller.show_screen("editor"))

        self.title_label = self.make_title("")
        self.subtitle_label = self.make_subtitle("")

        layout.addWidget(self.back_button)
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        layout.addSpacing(10)

        self.file_name_label = self.make_field_label("")
        self.file_name_input = QLineEdit()
        self.file_name_input.setMaxLength(60)

        layout.addWidget(self.file_name_label)
        layout.addWidget(self.file_name_input)

        self.save_location_label = self.make_field_label("")
        layout.addWidget(self.save_location_label)

        location = QFrame()
        location.setObjectName("statusBar")

        location_layout = QVBoxLayout(location)
        location_layout.setContentsMargins(12, 8, 12, 8)

        self.location_text = self.make_subtitle("")
        location_layout.addWidget(self.location_text)

        layout.addWidget(location)

        self.recent_files_label = self.make_field_label("")
        self.recent_files = QListWidget()
        self.recent_files.setMinimumHeight(120)
        self.recent_files.itemClicked.connect(self.use_recent_name)

        layout.addWidget(self.recent_files_label)
        layout.addWidget(self.recent_files)

        self.cancel_button = self.normal_button("")
        self.export_project_button = self.normal_button("")
        self.export_audio_button = self.normal_button("")
        self.save_button = self.primary_button("")

        self.cancel_button.clicked.connect(lambda: self.controller.show_screen("editor"))
        self.export_project_button.clicked.connect(self.export_project)
        self.export_audio_button.clicked.connect(self.export_audio)
        self.save_button.clicked.connect(self.save_project)

        layout.addLayout(
            self.horizontal_buttons(
                self.cancel_button,
                self.export_project_button,
                self.export_audio_button,
                self.save_button,
            )
        )

        self.center_card_layout(card)

    def refresh(self) -> None:
        self._apply_texts()
        self._load_current_project_name()
        self._load_recent_files()

    def use_recent_name(self, item: QListWidgetItem) -> None:
        project_name = item.data(Qt.UserRole)

        if not project_name:
            return

        self.file_name_input.setText(str(project_name))

    def save_project(self) -> None:
        project = self._validated_current_project()
        if project is None:
            return

        self.controller.storage.save_project_to_library(project)
        self.controller.set_current_project(project)

        QMessageBox.information(
            self,
            self._t("message_title"),
            self._t("saved"),
        )

        self.controller.show_screen("editor")

    def export_project(self) -> None:
        project = self._validated_current_project()
        if project is None:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self._t("export_project"),
            f"{project.name}.json",
            self._t("project_filter"),
        )

        if not file_path:
            return

        try:
            self.controller.storage.export_project_to_file(project, file_path)
        except Exception as error:
            self._show_export_error(error)
            return

        QMessageBox.information(
            self,
            self._t("message_title"),
            self._t("project_exported"),
        )

    def export_audio(self) -> None:
        project = self._validated_current_project()
        if project is None:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self._t("export_audio"),
            f"{project.name}.wav",
            self._t("audio_filter"),
        )

        if not file_path:
            return

        try:
            self.controller.storage.export_audio_to_file(project, file_path)
        except Exception as error:
            self._show_export_error(error)
            return

        QMessageBox.information(
            self,
            self._t("message_title"),
            self._t("audio_exported"),
        )

    def _validated_current_project(self) -> Project | None:
        project = self.controller.current_project

        if project is None:
            QMessageBox.warning(
                self,
                self._t("message_title"),
                self._t("no_project"),
            )
            return None

        name = self._normalized_project_name()

        if not name:
            QMessageBox.warning(
                self,
                self._t("message_title"),
                self._t("empty_name"),
            )
            return None

        project.name = name
        self.controller.set_current_project(project)
        return project

    def _show_export_error(self, error: Exception) -> None:
        QMessageBox.critical(
            self,
            self._t("message_title"),
            f"{self._t('export_error')}\n\n{error}",
        )

    def _load_current_project_name(self) -> None:
        project = self.controller.current_project or Project()

        self.file_name_input.setText(project.name)
        self.file_name_input.setPlaceholderText(self._t("file_placeholder"))

    def _load_recent_files(self) -> None:
        self.recent_files.clear()

        projects = self.controller.storage.load_saved_projects()[:5]

        if not projects:
            item = QListWidgetItem(self._t("no_recent"))
            item.setFlags(Qt.NoItemFlags)
            self.recent_files.addItem(item)
            return

        for saved_project in projects:
            date = self.controller.format_date(saved_project.saved_at or saved_project.created_at)

            item = QListWidgetItem(f"{saved_project.name}    |    {date}")
            item.setData(Qt.UserRole, saved_project.name)

            self.recent_files.addItem(item)

    def _apply_texts(self) -> None:
        self.back_button.setText(self._t("back"))
        self.title_label.setText(self._t("title"))
        self.subtitle_label.setText(self._t("subtitle"))
        self.file_name_label.setText(self._t("file_name"))
        self.save_location_label.setText(self._t("save_location"))
        self.location_text.setText(self._t("location"))
        self.recent_files_label.setText(self._t("recent_files"))
        self.cancel_button.setText(self._t("cancel"))
        self.export_project_button.setText(self._t("export_project"))
        self.export_audio_button.setText(self._t("export_audio"))
        self.save_button.setText(self._t("save"))

    def _normalized_project_name(self) -> str:
        return " ".join(self.file_name_input.text().strip().split())

    def _t(self, key: str) -> str:
        language = getattr(self.controller.settings, "language", "en")
        dictionary = TEXTS.get(language, TEXTS["en"])
        return dictionary[key]
