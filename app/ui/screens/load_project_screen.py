from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QLabel,
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
        "back_start": "←  Back to Start",
        "title": "Load Project",
        "subtitle": "Select a project to open",
        "saved_projects": "Saved Projects",
        "project_details": "Project Details",
        "select_details": "Select a project to view details",
        "no_projects": "No saved projects found",
        "back": "Back",
        "open": "📂  Open Project",
        "delete": "Delete",
        "warning_title": "Load Project",
        "select_first": "Select a project first.",
        "delete_title": "Delete Project",
        "import": "Import Project...",
        "imported": "Project imported successfully.",
        "import_error": "Could not import selected project file.",
        "unsupported_audio_import": "Import supports JSON and MIDI project files only. MP3/WAV are final audio files, so this app cannot convert them back into editable notes.",
        "delete_question": "Delete project '{name}'?",
        "details": (
            "Tempo: {tempo} BPM\n"
            "Number of Bars: {bars}\n"
            "Total Notes: {notes}\n"
            "Pitch Range: {pitch_range}\n"
            "Created: {created}\n"
            "Last Saved: {saved}"
        ),
    },
    "pl": {
        "back_start": "←  Powrót do menu",
        "title": "Wczytaj projekt",
        "subtitle": "Wybierz projekt do otwarcia",
        "saved_projects": "Zapisane projekty",
        "project_details": "Szczegóły projektu",
        "select_details": "Wybierz projekt, aby zobaczyć szczegóły",
        "no_projects": "Brak zapisanych projektów",
        "back": "Powrót",
        "open": "📂  Otwórz projekt",
        "delete": "Usuń",
        "import": "Importuj projekt...",
        "imported": "Projekt został zaimportowany.",
        "import_error": "Nie udało się zaimportować wybranego pliku projektu.",
        "unsupported_audio_import": "Import obsługuje tylko pliki projektu JSON i MIDI. MP3/WAV są gotowym audio, więc aplikacja nie zamienia ich z powrotem na edytowalne nuty.",
        "warning_title": "Wczytaj projekt",
        "select_first": "Najpierw wybierz projekt.",
        "delete_title": "Usuń projekt",
        "delete_question": "Usunąć projekt '{name}'?",
        "details": (
            "Tempo: {tempo} BPM\n"
            "Liczba taktów: {bars}\n"
            "Liczba nut: {notes}\n"
            "Zakres dźwięków: {pitch_range}\n"
            "Utworzono: {created}\n"
            "Ostatni zapis: {saved}"
        ),
    },
}


class LoadProjectScreen(BaseScreen):
    """Screen responsible for browsing, opening and deleting saved projects."""

    def __init__(self, controller: "MainWindow") -> None:
        super().__init__(controller)

        self.projects: list[Project] = []

        card = self.make_card(max_width=980)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(16)

        self.back_start_button = self.normal_button("")
        self.back_start_button.setMaximumWidth(190)
        self.back_start_button.clicked.connect(lambda: self.controller.show_screen("start"))

        self.title_label = self.make_title("")
        self.subtitle_label = self.make_subtitle("")

        layout.addWidget(self.back_start_button)
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        layout.addSpacing(8)

        content = QGridLayout()
        content.setHorizontalSpacing(22)
        content.setVerticalSpacing(8)

        self.saved_projects_label = self.make_field_label("")
        self.project_details_label = self.make_field_label("")

        content.addWidget(self.saved_projects_label, 0, 0)
        content.addWidget(self.project_details_label, 0, 1)

        self.project_list = QListWidget()
        self.project_list.setMinimumHeight(300)
        self.project_list.itemSelectionChanged.connect(self.update_details)

        content.addWidget(self.project_list, 1, 0)

        self.details_card = QFrame()
        self.details_card.setObjectName("card")

        details_layout = QVBoxLayout(self.details_card)
        details_layout.setContentsMargins(22, 20, 22, 20)
        details_layout.setSpacing(8)

        self.details_title = QLabel()
        self.details_title.setObjectName("sectionTitle")
        self.details_title.setWordWrap(True)

        self.details_body = QLabel()
        self.details_body.setObjectName("detailsBody")
        self.details_body.setTextFormat(Qt.PlainText)
        self.details_body.setAlignment(Qt.AlignTop)
        self.details_body.setWordWrap(True)

        details_layout.addWidget(self.details_title)
        details_layout.addWidget(self.details_body)
        details_layout.addStretch()

        content.addWidget(self.details_card, 1, 1)

        content.setColumnStretch(0, 1)
        content.setColumnStretch(1, 1)

        layout.addLayout(content)

        self.back_bottom_button = self.normal_button("")
        self.open_button = self.primary_button("")
        self.import_button = self.normal_button("")
        self.delete_button = self.normal_button("")
        self.delete_button.setObjectName("dangerButton")

        self.back_bottom_button.clicked.connect(lambda: self.controller.show_screen("start"))
        self.open_button.clicked.connect(self.open_selected_project)
        self.import_button.clicked.connect(self.import_project)
        self.delete_button.clicked.connect(self.delete_selected_project)

        layout.addLayout(
            self.horizontal_buttons(
                self.back_bottom_button,
                self.open_button,
                self.import_button,
                self.delete_button,
            )
        )

        self.center_card_layout(card)

    def refresh(self) -> None:
        self._apply_texts()
        self._load_projects()
        self.update_details()

    def selected_project(self) -> Project | None:
        row = self.project_list.currentRow()

        if row < 0 or row >= len(self.projects):
            return None

        return self.projects[row]

    def update_details(self) -> None:
        project = self.selected_project()
        has_project = project is not None

        self.open_button.setEnabled(has_project)
        self.delete_button.setEnabled(has_project)

        if project is None:
            self.details_title.setText(self._t("select_details"))
            self.details_body.setText("")
            return

        self.details_title.setText(project.name)
        self.details_body.setText(
            self._t("details").format(
                tempo=project.tempo,
                bars=project.bars,
                notes=len(project.notes),
                pitch_range=project.pitch_range,
                created=self.controller.format_date(project.created_at),
                saved=self.controller.format_date(project.saved_at or project.created_at),
            )
        )

    def open_selected_project(self) -> None:
        project = self.selected_project()

        if project is None:
            QMessageBox.warning(
                self,
                self._t("warning_title"),
                self._t("select_first"),
            )
            return

        self.controller.set_current_project(project)
        self.controller.show_screen("editor")

    def import_project(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self._t("import"),
            "",
            "Project files (*.json *.mid *.midi);;JSON files (*.json);;MIDI files (*.mid *.midi)",
        )

        if not file_path:
            return

        try:
            project = self.controller.storage.import_project_from_file(file_path)
            self.controller.storage.save_project_to_library(project)
            self.controller.set_current_project(project)
        except Exception as error:
            QMessageBox.critical(
                self,
                self._t("warning_title"),
                f"{self._t('import_error')}\n\n{error}",
            )
            return

        QMessageBox.information(
            self,
            self._t("warning_title"),
            self._t("imported"),
        )

        self.controller.show_screen("editor")

    def delete_selected_project(self) -> None:
        project = self.selected_project()

        if project is None:
            QMessageBox.warning(
                self,
                self._t("warning_title"),
                self._t("select_first"),
            )
            return

        response = QMessageBox.question(
            self,
            self._t("delete_title"),
            self._t("delete_question").format(name=project.name),
        )

        if response != QMessageBox.Yes:
            return

        self.controller.storage.delete_project(project.name)

        if (
            self.controller.current_project is not None
            and self.controller.current_project.name == project.name
        ):
            self.controller.current_project = None

        self.refresh()

    def _load_projects(self) -> None:
        self.projects = self.controller.storage.load_saved_projects()
        self.project_list.clear()

        if not self.projects:
            item = QListWidgetItem(self._t("no_projects"))
            item.setFlags(Qt.NoItemFlags)
            self.project_list.addItem(item)
            return

        for project in self.projects:
            date = self.controller.format_date(project.saved_at or project.created_at)
            self.project_list.addItem(QListWidgetItem(f"🎵  {project.name}\n    {date}"))

        self.project_list.setCurrentRow(0)

    def _apply_texts(self) -> None:
        self.back_start_button.setText(self._t("back_start"))
        self.title_label.setText(self._t("title"))
        self.subtitle_label.setText(self._t("subtitle"))
        self.saved_projects_label.setText(self._t("saved_projects"))
        self.project_details_label.setText(self._t("project_details"))
        self.back_bottom_button.setText(self._t("back"))
        self.open_button.setText(self._t("open"))
        self.import_button.setText(self._t("import"))
        self.delete_button.setText(self._t("delete"))

    def _t(self, key: str) -> str:
        language = getattr(self.controller.settings, "language", "en")
        dictionary = TEXTS.get(language, TEXTS["en"])
        return dictionary[key]