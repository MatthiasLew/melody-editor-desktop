from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout

from app.ui.screens.base import BaseScreen

if TYPE_CHECKING:
    from app.main import MainWindow


TEXTS = {
    "en": {
        "back": "←  Back to Start",
        "title": "Help",
        "subtitle": "Basic instructions for using Melody Editor",
        "body": (
            "1. Create a new project or load an existing one.\n"
            "2. In the editor, click an empty grid cell to add a note.\n"
            "3. Click a note to select it. Use arrow keys to move it.\n"
            "4. Press Delete or right-click a note to remove it.\n"
            "5. Use Play/Stop to preview the timeline animation.\n"
            "6. Save writes the project locally as a JSON file."
        ),
    },
    "pl": {
        "back": "←  Powrót do menu",
        "title": "Pomoc",
        "subtitle": "Podstawowa instrukcja obsługi Melody Editor",
        "body": (
            "1. Utwórz nowy projekt albo wczytaj istniejący.\n"
            "2. W edytorze kliknij puste pole siatki, aby dodać nutę.\n"
            "3. Kliknij nutę, aby ją zaznaczyć. Użyj strzałek, aby ją przesunąć.\n"
            "4. Naciśnij Delete albo kliknij nutę prawym przyciskiem, aby ją usunąć.\n"
            "5. Użyj Play/Stop, aby zobaczyć animację linii czasu.\n"
            "6. Zapis projektu działa lokalnie w pliku JSON."
        ),
    },
}


class HelpScreen(BaseScreen):
    """Help screen displayed inside the main application window."""

    def __init__(self, controller: "MainWindow") -> None:
        super().__init__(controller)

        card = self.make_card(max_width=760)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(42, 36, 42, 36)
        layout.setSpacing(18)

        self.back_button = self.normal_button("")
        self.back_button.setMaximumWidth(190)
        self.back_button.clicked.connect(lambda: self.controller.show_screen("start"))

        self.title_label = self.make_title("")
        self.subtitle_label = self.make_subtitle("")

        self.body_label = QLabel()
        self.body_label.setObjectName("detailsBody")
        self.body_label.setTextFormat(Qt.PlainText)
        self.body_label.setWordWrap(True)
        self.body_label.setAlignment(Qt.AlignTop)

        layout.addWidget(self.back_button)
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        layout.addWidget(self.body_label)
        layout.addStretch()

        self.center_card_layout(card)

    def refresh(self) -> None:
        self.back_button.setText(self._t("back"))
        self.title_label.setText(self._t("title"))
        self.subtitle_label.setText(self._t("subtitle"))
        self.body_label.setText(self._t("body"))

    def _t(self, key: str) -> str:
        language = getattr(self.controller.settings, "language", "en")
        dictionary = TEXTS.get(language, TEXTS["en"])
        return dictionary[key]