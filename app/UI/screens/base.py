from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

if TYPE_CHECKING:
    from app.main import MainWindow


class BaseScreen(QWidget):
    """Base class for all application screens."""

    def __init__(self, controller: "MainWindow") -> None:
        super().__init__()
        self.controller = controller
        self.setObjectName("appRoot")

    def refresh(self) -> None:
        """Called by MainWindow before displaying the screen."""

    def make_card(self, max_width: int | None = None) -> QFrame:
        card = QFrame()
        card.setObjectName("card")

        if max_width is not None:
            card.setMaximumWidth(max_width)

        return card

    def make_title(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("title")
        label.setWordWrap(True)
        return label

    def make_subtitle(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("subtitle")
        label.setWordWrap(True)
        return label

    def make_body_text(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("detailsBody")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignTop)
        return label

    def make_field_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("fieldLabel")
        label.setWordWrap(True)
        return label

    def make_section_title(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("sectionTitle")
        label.setWordWrap(True)
        return label

    def primary_button(self, text: str) -> QPushButton:
        button = self.normal_button(text)
        button.setObjectName("primaryButton")
        return button

    def danger_button(self, text: str) -> QPushButton:
        button = self.normal_button(text)
        button.setObjectName("dangerButton")
        return button

    def back_button(self, text: str = "← Back") -> QPushButton:
        button = self.normal_button(text)
        button.setMaximumWidth(180)
        return button

    def normal_button(self, text: str) -> QPushButton:
        button = QPushButton(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(42)
        return button

    def center_card_layout(self, card: QFrame, margin: int = 36) -> QVBoxLayout:
        if self.layout() is not None:
            raise RuntimeError("BaseScreen layout has already been initialized.")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(margin, margin, margin, margin)
        outer.setAlignment(Qt.AlignCenter)
        outer.addWidget(card)

        return outer

    def horizontal_buttons(self, *buttons: QPushButton) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(14)

        for button in buttons:
            button.setMinimumHeight(42)
            layout.addWidget(button)

        return layout