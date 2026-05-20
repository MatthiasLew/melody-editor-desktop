from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout

from app.ui.screens.base import BaseScreen

if TYPE_CHECKING:
    from app.main import MainWindow


TEXTS = {
    "en": {
        "title": "Melody Editor",
        "subtitle": "Simple music composition for students",
        "new_project": "♫  New Project",
        "load_project": "▣  Load Project",
        "settings": "⚙  Settings",
        "help": "?  Help",
        "exit": "↳  Exit",
    },
    "pl": {
        "title": "Melody Editor",
        "subtitle": "Proste tworzenie melodii",
        "new_project": "♫  Nowy projekt",
        "load_project": "▣  Wczytaj projekt",
        "settings": "⚙  Ustawienia",
        "help": "?  Pomoc",
        "exit": "↳  Wyjście",
    },
}


class StartScreen(BaseScreen):
    """Start screen used as the main navigation menu."""

    def __init__(self, controller: "MainWindow") -> None:
        super().__init__(controller)

        card = self.make_card(max_width=420)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(46, 42, 46, 42)
        card_layout.setSpacing(14)

        self.icon_label = QLabel("♫")
        self.icon_label.setObjectName("menuIcon")
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.title_label = self.make_title("")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.subtitle_label = self.make_subtitle("")
        self.subtitle_label.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(self.icon_label)
        card_layout.addWidget(self.title_label)
        card_layout.addWidget(self.subtitle_label)
        card_layout.addSpacing(24)

        self.new_project_button = self.primary_button("")
        self.load_project_button = self.normal_button("")
        self.settings_button = self.normal_button("")
        self.help_button = self.normal_button("")
        self.exit_button = self.normal_button("")

        buttons = [
            self.new_project_button,
            self.load_project_button,
            self.settings_button,
            self.help_button,
            self.exit_button,
        ]

        for button in buttons:
            button.setMinimumHeight(44)
            card_layout.addWidget(button)

        card_layout.addSpacing(4)

        self.new_project_button.clicked.connect(lambda: self.controller.show_screen("new_project"))
        self.load_project_button.clicked.connect(lambda: self.controller.show_screen("load_project"))
        self.settings_button.clicked.connect(lambda: self.controller.show_screen("settings"))
        self.help_button.clicked.connect(lambda: self.controller.show_screen("help"))
        self.exit_button.clicked.connect(self.controller.close)

        self.center_card_layout(card)

    def refresh(self) -> None:
        self.title_label.setText(self._t("title"))
        self.subtitle_label.setText(self._t("subtitle"))
        self.new_project_button.setText(self._t("new_project"))
        self.load_project_button.setText(self._t("load_project"))
        self.settings_button.setText(self._t("settings"))
        self.help_button.setText(self._t("help"))
        self.exit_button.setText(self._t("exit"))

    def _t(self, key: str) -> str:
        language = getattr(self.controller.settings, "language", "en")
        dictionary = TEXTS.get(language, TEXTS["en"])
        return dictionary[key]