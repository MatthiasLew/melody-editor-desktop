from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.core.audio import AudioEngine
from app.core.models import Project
from app.ui.screens.base import BaseScreen
from app.ui.widgets import MelodyGridWidget

if TYPE_CHECKING:
    from app.main import MainWindow

TEXTS = {
    "en": {
        "home": "⌂",
        "play": "▶  Play",
        "stop": "■  Stop",
        "save": "▣  Save",
        "hint": "Click grid to add notes. Select note and use arrows/Delete. Right-click removes note.",
        "status": "Tempo: {tempo} BPM     Notes: {notes}     {bars} Bars",
        "start_step": "Start step",
        "loop": "Loop",
        "start_step_tooltip": "Choose the timeline step where playback should start.",
        "loop_tooltip": "Repeats playback after reaching the end of the melody.",
    },
    "pl": {
        "home": "⌂",
        "play": "▶  Odtwórz",
        "stop": "■  Stop",
        "save": "▣  Zapisz",
        "hint": "Kliknij siatkę, aby dodać nutę. Zaznacz nutę i użyj strzałek/Delete. Prawy klik usuwa nutę.",
        "status": "Tempo: {tempo} BPM     Nuty: {notes}     Takty: {bars}",
        "start_step": "Start",
        "loop": "Pętla",
        "start_step_tooltip": "Wybierz krok osi czasu, od którego ma rozpocząć się odtwarzanie.",
        "loop_tooltip": "Powtarza odtwarzanie po dojściu do końca melodii.",
    },
}


class EditorScreen(BaseScreen):
    """Main melody editing screen with clickable grid and playback preview."""

    def __init__(self, controller: "MainWindow") -> None:
        super().__init__(controller)

        self.is_playing = False
        self.current_step = 0
        self.playback_start_step = 0
        self.loop_enabled = False

        self.audio = AudioEngine(self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advance_playback)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.toolbar = QFrame()
        self.toolbar.setObjectName("toolbar")

        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(22, 10, 22, 10)
        toolbar_layout.setSpacing(12)

        self.home_button = self.normal_button("⌂")
        self.home_button.setFixedWidth(48)
        self.home_button.clicked.connect(self.go_to_start)

        self.project_label = QLabel("Untitled Project")
        self.project_label.setObjectName("fieldLabel")

        project_font = QFont("Segoe UI")
        project_font.setPointSize(12)
        project_font.setBold(True)
        self.project_label.setFont(project_font)

        toolbar_layout.addWidget(self.home_button)
        toolbar_layout.addWidget(self.project_label)
        toolbar_layout.addStretch()

        self.start_step_label = QLabel("")
        self.start_step_label.setObjectName("fieldLabel")

        self.start_step_input = QSpinBox()
        self.start_step_input.setRange(0, 0)
        self.start_step_input.setMinimumWidth(90)
        self.start_step_input.setAlignment(Qt.AlignCenter)
        self.start_step_input.valueChanged.connect(self.set_playback_start_step)

        self.loop_checkbox = QCheckBox("")
        self.loop_checkbox.toggled.connect(self.set_loop_enabled)

        self.play_button = self.normal_button("▶  Play")
        self.play_button.setObjectName("playButton")
        self.play_button.clicked.connect(self.toggle_playback)

        self.save_button = self.normal_button("▣  Save")
        self.save_button.clicked.connect(self.go_to_save)

        toolbar_layout.addWidget(self.start_step_label)
        toolbar_layout.addWidget(self.start_step_input)
        toolbar_layout.addWidget(self.loop_checkbox)
        toolbar_layout.addWidget(self.play_button)
        toolbar_layout.addWidget(self.save_button)

        outer.addWidget(self.toolbar)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(26, 24, 26, 24)
        body_layout.setSpacing(0)

        grid_card = QFrame()
        grid_card.setObjectName("card")

        grid_layout = QVBoxLayout(grid_card)
        grid_layout.setContentsMargins(18, 18, 18, 18)

        self.grid = MelodyGridWidget()
        self.grid.notes_changed.connect(self.sync_notes_to_project)

        grid_layout.addWidget(self.grid)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(grid_card)

        body_layout.addWidget(scroll)
        outer.addWidget(body, stretch=1)

        self.status = QFrame()
        self.status.setObjectName("statusBar")

        status_layout = QHBoxLayout(self.status)
        status_layout.setContentsMargins(22, 9, 22, 9)

        self.info_label = QLabel()
        self.info_label.setObjectName("fieldLabel")

        self.hint_label = QLabel()
        self.hint_label.setObjectName("subtitle")

        status_layout.addWidget(self.info_label)
        status_layout.addStretch()
        status_layout.addWidget(self.hint_label)

        outer.addWidget(self.status)

    def refresh(self) -> None:
        self.stop_playback()

        project = self._get_or_create_project()

        self.grid.set_dark_theme(self._is_black_theme())
        self.grid.set_keyboard_shortcuts_enabled(
            self.controller.settings.keyboard_shortcuts
        )
        self.grid.set_project_data(
            notes=project.notes,
            bars=project.bars,
            pitch_range=project.pitch_range,
        )
        max_step = max(0, self.grid.columns - 1)
        self.playback_start_step = min(self.playback_start_step, max_step)

        self.start_step_input.blockSignals(True)
        self.start_step_input.setRange(0, max_step)
        self.start_step_input.setValue(self.playback_start_step)
        self.start_step_input.blockSignals(False)

        self.project_label.setText(project.name)
        self._apply_texts()
        self.update_status()

    def sync_notes_to_project(self) -> None:
        project = self._get_or_create_project()
        project.notes = self.grid.notes

        self.controller.set_current_project(project)
        self.update_status()

    def update_status(self) -> None:
        project = self._get_or_create_project()

        self.info_label.setText(
            self._t("status").format(
                tempo=project.tempo,
                notes=len(project.notes),
                bars=project.bars,
            )
        )

        def set_playback_start_step(self, value: int) -> None:
            max_step = max(0, self.grid.columns - 1)
            self.playback_start_step = min(max(0, int(value)), max_step)

            if not self.is_playing:
                self.grid.set_playback_step(self.playback_start_step)

        def set_loop_enabled(self, enabled: bool) -> None:
            self.loop_enabled = bool(enabled)
        def set_playback_start_step(self, value: int) -> None:
            max_step = max(0, self.grid.columns - 1)
            self.playback_start_step = min(max(0, value), max_step)

            if not self.is_playing:
                self.grid.set_playback_step(self.playback_start_step)

        def set_loop_enabled(self, enabled: bool) -> None:
            self.loop_checkbox.setChecked(enabled)

    def toggle_playback(self) -> None:
        if self.is_playing:
            self.stop_playback()
            return

        self.start_playback()

    def start_playback(self) -> None:
        project = self._get_or_create_project()

        self.is_playing = True
        self.current_step = min(
            max(0, self.playback_start_step),
            max(0, self.grid.columns - 1),
        )
        self.grid.set_playback_step(self.current_step)
        self._play_current_step_notes()

        self.play_button.setObjectName("dangerButton")
        self.play_button.setText(self._t("stop"))
        self._repolish(self.play_button)

        interval_ms = max(80, int(60000 / max(1, project.tempo)))
        self.timer.start(interval_ms)

    def stop_playback(self) -> None:
        self.is_playing = False
        self.timer.stop()
        self.current_step = 0

        self.grid.set_playback_step(self.playback_start_step)

        self.play_button.setObjectName("playButton")
        self.play_button.setText(self._t("play"))
        self._repolish(self.play_button)

    def advance_playback(self) -> None:
        self.current_step += 1

        if self.current_step >= self.grid.columns:
            if self.loop_enabled:
                self.current_step = self.playback_start_step
            else:
                self.stop_playback()
                return

        self.grid.set_playback_step(self.current_step)
        self._play_current_step_notes()

    def _play_current_step_notes(self) -> None:
        project = self._get_or_create_project()

        note_names: list[str] = []

        for note in project.notes:
            if note.time != self.current_step:
                continue

            note_name = self.grid.note_name_for_pitch(note.pitch)

            if note_name is not None:
                note_names.append(note_name)

        if not note_names:
            return

        self.audio.play_notes(
            note_names=note_names,
            volume=self.controller.settings.volume,
        )

    def go_to_save(self) -> None:
        self.stop_playback()
        self.sync_notes_to_project()
        self.controller.show_screen("save_project")

    def go_to_start(self) -> None:
        self.stop_playback()
        self.sync_notes_to_project()
        self.controller.show_screen("start")

    def _get_or_create_project(self) -> Project:
        if self.controller.current_project is None:
            self.controller.set_current_project(Project())

        return self.controller.current_project

    def _apply_texts(self) -> None:
        self.start_step_label.setText(self._t("start_step"))
        self.loop_checkbox.setText(self._t("loop"))
        self.start_step_input.setToolTip(self._t("start_step_tooltip"))
        self.loop_checkbox.setToolTip(self._t("loop_tooltip"))
        self.home_button.setText(self._t("home"))
        self.save_button.setText(self._t("save"))
        self.hint_label.setText(self._t("hint"))

        if self.is_playing:
            self.play_button.setText(self._t("stop"))
        else:
            self.play_button.setText(self._t("play"))

    def _t(self, key: str) -> str:
        language = getattr(self.controller.settings, "language", "en")
        dictionary = TEXTS.get(language, TEXTS["en"])
        return dictionary[key]

    def _is_black_theme(self) -> bool:
        return self.controller.settings.theme in {"black", "dark"}

    @staticmethod
    def _repolish(widget: QWidget) -> None:
        widget.style().unpolish(widget)
        widget.style().polish(widget)
