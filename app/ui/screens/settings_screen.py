from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from app.core.models import AppSettings
from app.ui.screens.base import BaseScreen
from app.ui.widgets import ReadableSpinBox

if TYPE_CHECKING:
    from app.main import MainWindow

TEXTS = {
    "en": {
        "back": "←  Back to Start",
        "title": "Settings",
        "subtitle": "Appearance changes are previewed immediately. Back discards unsaved changes.",
        "audio": "Audio Settings",
        "volume": "Volume",
        "appearance": "Appearance",
        "theme": "Theme",
        "theme_light": "Light",
        "theme_black": "Black",
        "language": "Language",
        "project_defaults": "Project Defaults",
        "default_tempo": "Default Tempo (BPM)",
        "accessibility": "Accessibility Options",
        "high_contrast": "High Contrast Mode",
        "large_text": "Large Text",
        "keyboard_shortcuts": "Keyboard Shortcuts",
        "cancel": "Back",
        "save": "Save and Back",
        "volume_tooltip": "Controls melody playback volume.",
        "theme_tooltip": "Previews the application theme immediately. Use Save and Back to keep the change.",
        "language_tooltip": "Previews the interface language immediately. Use Save and Back to keep the change.",
        "default_tempo_tooltip": "Default tempo for new projects. Allowed range: 40–240 BPM.",
        "high_contrast_tooltip": "Previews high contrast immediately. Use Save and Back to keep the change.",
        "large_text_tooltip": "Previews larger interface text immediately. Use Save and Back to keep the change.",
        "keyboard_shortcuts_tooltip": "Enables keyboard shortcuts in the editor, for example arrows to move notes and Delete to remove them.",
    },
    "pl": {
        "back": "←  Powrót do menu",
        "title": "Ustawienia",
        "subtitle": "Wygląd zmienia się od razu jako podgląd. Powrót odrzuca niezapisane zmiany.",
        "audio": "Ustawienia dźwięku",
        "volume": "Głośność",
        "appearance": "Wygląd",
        "theme": "Motyw",
        "theme_light": "Jasny",
        "theme_black": "Czarny",
        "language": "Język",
        "project_defaults": "Domyślne ustawienia projektu",
        "default_tempo": "Domyślne tempo (BPM)",
        "accessibility": "Opcje dostępności",
        "high_contrast": "Wysoki kontrast",
        "large_text": "Duży tekst",
        "keyboard_shortcuts": "Skróty klawiaturowe",
        "cancel": "Powrót",
        "save": "Zapisz i wróć",
        "volume_tooltip": "Ustawia głośność odtwarzania melodii.",
        "theme_tooltip": "Pokazuje motyw od razu. Kliknij Zapisz i wróć, aby zachować zmianę.",
        "language_tooltip": "Pokazuje język od razu. Kliknij Zapisz i wróć, aby zachować zmianę.",
        "default_tempo_tooltip": "Domyślne tempo dla nowych projektów. Dozwolony zakres: 40–240 BPM.",
        "high_contrast_tooltip": "Pokazuje wysoki kontrast od razu. Kliknij Zapisz i wróć, aby zachować zmianę.",
        "large_text_tooltip": "Pokazuje większy tekst od razu. Kliknij Zapisz i wróć, aby zachować zmianę.",
        "keyboard_shortcuts_tooltip": "Włącza skróty klawiaturowe w edytorze, np. strzałki do przesuwania nut i Delete do usuwania.",
    },
}


class SettingsScreen(BaseScreen):
    """Screen used to configure application preferences."""

    def __init__(self, controller: "MainWindow") -> None:
        super().__init__(controller)

        self._is_refreshing = False
        self._saved_settings_snapshot = AppSettings()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 28, 28, 28)
        outer.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        outer.addWidget(self.scroll_area)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(0)
        scroll_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.scroll_area.setWidget(scroll_content)

        card = self.make_card(max_width=900)
        card.setMinimumWidth(720)
        scroll_layout.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(42, 36, 42, 36)
        layout.setSpacing(18)

        self.back_button = self.normal_button("")
        self.back_button.setMaximumWidth(210)
        self.back_button.clicked.connect(self.discard_changes)

        self.title_label = self.make_title("")
        self.subtitle_label = self.make_subtitle("")

        layout.addWidget(self.back_button)
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        layout.addSpacing(8)

        self.audio_title = self.make_section_title("")
        layout.addWidget(self.audio_title)

        volume_row = QHBoxLayout()
        volume_row.setSpacing(12)

        self.volume_label = self.make_field_label("")
        self.volume_value = QLabel("75%")
        self.volume_value.setObjectName("fieldLabel")

        volume_row.addWidget(self.volume_label)
        volume_row.addStretch()
        volume_row.addWidget(self.volume_value)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(75)
        self.volume_slider.valueChanged.connect(self._update_volume_label)
        self.volume_slider.valueChanged.connect(self._handle_live_settings_changed)

        layout.addLayout(volume_row)
        layout.addWidget(self.volume_slider)

        layout.addSpacing(10)

        self.appearance_title = self.make_section_title("")
        layout.addWidget(self.appearance_title)

        self.theme_label = self.make_field_label("")
        self.theme_input = QComboBox()
        self.theme_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.theme_input.currentIndexChanged.connect(self._handle_live_settings_changed)

        self.language_label = self.make_field_label("")
        self.language_input = QComboBox()
        self.language_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.language_input.addItem("English", "en")
        self.language_input.addItem("Polski", "pl")
        self.language_input.currentIndexChanged.connect(self._handle_language_preview)

        layout.addWidget(self.theme_label)
        layout.addWidget(self.theme_input)
        layout.addWidget(self.language_label)
        layout.addWidget(self.language_input)

        layout.addSpacing(10)

        self.project_defaults_title = self.make_section_title("")
        layout.addWidget(self.project_defaults_title)

        self.default_tempo_label = self.make_field_label("")
        self.default_tempo_input = ReadableSpinBox()
        self.default_tempo_input.setRange(40, 240)
        self.default_tempo_input.setValue(120)
        self.default_tempo_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.default_tempo_input.valueChanged.connect(self._handle_live_settings_changed)

        layout.addWidget(self.default_tempo_label)
        layout.addWidget(self.default_tempo_input)

        layout.addSpacing(10)

        self.accessibility_title = self.make_section_title("")
        layout.addWidget(self.accessibility_title)

        self.high_contrast = QCheckBox()
        self.large_text = QCheckBox()
        self.keyboard_shortcuts = QCheckBox()

        self.high_contrast.toggled.connect(self._handle_live_settings_changed)
        self.large_text.toggled.connect(self._handle_live_settings_changed)
        self.keyboard_shortcuts.toggled.connect(self._handle_live_settings_changed)

        layout.addWidget(self.high_contrast)
        layout.addWidget(self.large_text)
        layout.addWidget(self.keyboard_shortcuts)

        layout.addSpacing(10)

        self.cancel_button = self.normal_button("")
        self.save_button = self.primary_button("")

        self.cancel_button.clicked.connect(self.discard_changes)
        self.save_button.clicked.connect(self.save_settings)

        layout.addLayout(self.horizontal_buttons(self.cancel_button, self.save_button))

    def refresh(self) -> None:
        self._is_refreshing = True

        # Snapshot is the last saved/accepted state. Live changes below are only a preview.
        self._saved_settings_snapshot = AppSettings.from_dict(self.controller.settings.to_dict())
        settings = self._saved_settings_snapshot

        self._set_combo_value(self.language_input, settings.language)

        self.volume_slider.setValue(settings.volume)
        self._update_volume_label(settings.volume)

        self.default_tempo_input.setValue(settings.default_tempo)
        self.high_contrast.setChecked(settings.high_contrast)
        self.large_text.setChecked(settings.large_text)
        self.keyboard_shortcuts.setChecked(settings.keyboard_shortcuts)

        self._apply_texts()
        self._populate_theme_input(settings.theme)
        self._apply_tooltips()

        self._is_refreshing = False

    def save_settings(self) -> None:
        settings = self._current_form_settings()
        self.controller.settings = settings
        self.controller.storage.save_settings(settings)
        self.controller.apply_current_styles()
        self.controller.show_screen("start")

    def discard_changes(self) -> None:
        self.controller.settings = AppSettings.from_dict(self._saved_settings_snapshot.to_dict())
        self.controller.apply_current_styles()
        self.controller.show_screen("start")

    def _current_form_settings(self) -> AppSettings:
        return AppSettings(
            language=str(self.language_input.currentData()),
            volume=int(self.volume_slider.value()),
            theme=str(self.theme_input.currentData()),
            default_tempo=int(self.default_tempo_input.value()),
            high_contrast=self.high_contrast.isChecked(),
            large_text=self.large_text.isChecked(),
            keyboard_shortcuts=self.keyboard_shortcuts.isChecked(),
        )

    def _preview_current_settings(self) -> None:
        self.controller.settings = self._current_form_settings()
        self.controller.apply_current_styles()

    def _handle_live_settings_changed(self, *_: object) -> None:
        if self._is_refreshing:
            return

        self._preview_current_settings()

    def _handle_language_preview(self, *_: object) -> None:
        if self._is_refreshing:
            return

        self._apply_texts()
        self._apply_tooltips()
        self._preview_current_settings()

    def _apply_tooltips(self) -> None:
        self.volume_slider.setToolTip(self._t("volume_tooltip"))
        self.theme_input.setToolTip(self._t("theme_tooltip"))
        self.language_input.setToolTip(self._t("language_tooltip"))
        self.default_tempo_input.setToolTip(self._t("default_tempo_tooltip"))

        self.high_contrast.setToolTip(self._t("high_contrast_tooltip"))
        self.large_text.setToolTip(self._t("large_text_tooltip"))
        self.keyboard_shortcuts.setToolTip(self._t("keyboard_shortcuts_tooltip"))

    def _apply_texts(self) -> None:
        current_theme = str(self.theme_input.currentData() or self.controller.settings.theme)

        self.back_button.setText(self._t("back"))
        self.title_label.setText(self._t("title"))
        self.subtitle_label.setText(self._t("subtitle"))

        self.audio_title.setText(self._t("audio"))
        self.volume_label.setText(self._t("volume"))

        self.appearance_title.setText(self._t("appearance"))
        self.theme_label.setText(self._t("theme"))
        self.language_label.setText(self._t("language"))

        self.project_defaults_title.setText(self._t("project_defaults"))
        self.default_tempo_label.setText(self._t("default_tempo"))

        self.accessibility_title.setText(self._t("accessibility"))
        self.high_contrast.setText(self._t("high_contrast"))
        self.large_text.setText(self._t("large_text"))
        self.keyboard_shortcuts.setText(self._t("keyboard_shortcuts"))

        self.cancel_button.setText(self._t("cancel"))
        self.save_button.setText(self._t("save"))

        self._populate_theme_input(current_theme)

    def _populate_theme_input(self, selected_theme: str) -> None:
        normalized_theme = "black" if selected_theme == "dark" else selected_theme

        self.theme_input.blockSignals(True)
        self.theme_input.clear()

        self.theme_input.addItem(self._t("theme_light"), "light")
        self.theme_input.addItem(self._t("theme_black"), "black")

        self._set_combo_value(self.theme_input, normalized_theme)

        self.theme_input.blockSignals(False)

    def _update_volume_label(self, value: int) -> None:
        self.volume_value.setText(f"{value}%")

    @staticmethod
    def _set_combo_value(combo_box: QComboBox, value: str) -> None:
        index = combo_box.findData(value)
        combo_box.setCurrentIndex(index if index >= 0 else 0)

    def _t(self, key: str) -> str:
        language = str(self.language_input.currentData() or self.controller.settings.language)
        dictionary = TEXTS.get(language, TEXTS["en"])
        return dictionary[key]
