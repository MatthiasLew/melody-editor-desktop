from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QFormLayout, QHBoxLayout, QLineEdit, QSpinBox, QVBoxLayout

from app.core.models import Project
from app.ui.screens.base import BaseScreen

if TYPE_CHECKING:
    from app.main import MainWindow


TEXTS = {
    "en": {
        "back": "←  Back to Start",
        "title": "New Project",
        "subtitle": "Configure your melody project settings",
        "project_name": "Project Name",
        "tempo_bars": "Tempo (BPM) / Number of Bars",
        "pitch_range": "Pitch Range",
        "cancel": "Cancel",
        "create": "Create Project",
        "default_project_name": "Untitled Project",
        "name_placeholder": "Enter project name",
        "pitch_low": "Low (C3 - C5)",
        "pitch_medium": "Medium (C4 - C6)",
        "pitch_high": "High (C5 - C7)",
    },
    "pl": {
        "back": "←  Powrót do menu",
        "title": "Nowy projekt",
        "subtitle": "Skonfiguruj ustawienia projektu melodii",
        "project_name": "Nazwa projektu",
        "tempo_bars": "Tempo (BPM) / Liczba taktów",
        "pitch_range": "Zakres dźwięków",
        "cancel": "Anuluj",
        "create": "Utwórz projekt",
        "default_project_name": "Nowy projekt",
        "name_placeholder": "Wpisz nazwę projektu",
        "pitch_low": "Niski (C3 - C5)",
        "pitch_medium": "Średni (C4 - C6)",
        "pitch_high": "Wysoki (C5 - C7)",
    },
}


class NewProjectScreen(BaseScreen):
    """Screen used to configure and create a new melody project."""

    def __init__(self, controller: "MainWindow") -> None:
        super().__init__(controller)

        card = self.make_card(max_width=720)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(42, 36, 42, 36)
        layout.setSpacing(20)

        self.back_button = self.normal_button("")
        self.back_button.setMaximumWidth(190)
        self.back_button.clicked.connect(lambda: self.controller.show_screen("start"))

        self.title_label = self.make_title("")
        self.subtitle_label = self.make_subtitle("")

        layout.addWidget(self.back_button)
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        layout.addSpacing(10)

        self.project_name_input = QLineEdit()
        self.project_name_input.setMinimumHeight(42)
        self.project_name_input.setMaxLength(60)

        self.tempo_input = QSpinBox()
        self.tempo_input.setRange(40, 240)
        self.tempo_input.setValue(120)

        self.bars_input = QSpinBox()
        self.bars_input.setRange(1, 64)
        self.bars_input.setValue(8)

        self.pitch_range_input = QComboBox()

        self.project_name_label = self.make_field_label("")
        self.tempo_bars_label = self.make_field_label("")
        self.pitch_range_label = self.make_field_label("")

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(14)

        form.addRow(self.project_name_label, self.project_name_input)

        tempo_bars_row = QHBoxLayout()
        tempo_bars_row.setSpacing(20)
        tempo_bars_row.addWidget(self.tempo_input)
        tempo_bars_row.addWidget(self.bars_input)

        form.addRow(self.tempo_bars_label, tempo_bars_row)
        form.addRow(self.pitch_range_label, self.pitch_range_input)

        layout.addLayout(form)
        layout.addSpacing(8)

        self.cancel_button = self.normal_button("")
        self.create_button = self.primary_button("")

        self.cancel_button.clicked.connect(lambda: self.controller.show_screen("start"))
        self.create_button.clicked.connect(self.create_project)

        layout.addLayout(self.horizontal_buttons(self.cancel_button, self.create_button))

        self.center_card_layout(card)

    def refresh(self) -> None:
        self._apply_texts()
        self._reset_form()

    def create_project(self) -> None:
        name = self.project_name_input.text().strip()

        if not name:
            name = self._t("default_project_name")

        project = Project(
            name=name,
            tempo=int(self.tempo_input.value()),
            bars=int(self.bars_input.value()),
            pitch_range=str(self.pitch_range_input.currentData()),
            notes=[],
        )

        self.controller.set_current_project(project)
        self.controller.show_screen("editor")

    def _reset_form(self) -> None:
        self.project_name_input.setText(self._t("default_project_name"))
        self.project_name_input.setPlaceholderText(self._t("name_placeholder"))

        self.tempo_input.setValue(int(self.controller.settings.default_tempo))
        self.bars_input.setValue(8)

        self._populate_pitch_ranges()
        self.pitch_range_input.setCurrentIndex(1)

    def _populate_pitch_ranges(self) -> None:
        current_value = self.pitch_range_input.currentData() or "c4-c6"

        self.pitch_range_input.blockSignals(True)
        self.pitch_range_input.clear()

        self.pitch_range_input.addItem(self._t("pitch_low"), "c3-c5")
        self.pitch_range_input.addItem(self._t("pitch_medium"), "c4-c6")
        self.pitch_range_input.addItem(self._t("pitch_high"), "c5-c7")

        index = self.pitch_range_input.findData(current_value)
        self.pitch_range_input.setCurrentIndex(index if index >= 0 else 1)

        self.pitch_range_input.blockSignals(False)

    def _apply_texts(self) -> None:
        self.back_button.setText(self._t("back"))
        self.title_label.setText(self._t("title"))
        self.subtitle_label.setText(self._t("subtitle"))
        self.project_name_label.setText(self._t("project_name"))
        self.tempo_bars_label.setText(self._t("tempo_bars"))
        self.pitch_range_label.setText(self._t("pitch_range"))
        self.cancel_button.setText(self._t("cancel"))
        self.create_button.setText(self._t("create"))

    def _t(self, key: str) -> str:
        language = getattr(self.controller.settings, "language", "en")
        dictionary = TEXTS.get(language, TEXTS["en"])
        return dictionary[key]