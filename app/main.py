from __future__ import annotations

import logging
import sys
from datetime import datetime

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from app.core.models import AppSettings, Project
from app.core.storage import Storage
from app.ui.screens.editor_screen import EditorScreen
from app.ui.screens.help_screen import HelpScreen
from app.ui.screens.load_project_screen import LoadProjectScreen
from app.ui.screens.new_project_screen import NewProjectScreen
from app.ui.screens.save_project_screen import SaveProjectScreen
from app.ui.screens.settings_screen import SettingsScreen
from app.ui.screens.start_screen import StartScreen
from app.ui.styles import build_stylesheet


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s",
)

LOGGER = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window responsible for screen navigation and shared state."""

    START_SCREEN = "start"

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Melody Editor")
        self.resize(1280, 760)
        self.setMinimumSize(1100, 700)

        self.storage = Storage()
        self.settings: AppSettings = self._load_settings_safe()
        self.current_project: Project | None = self._load_current_project_safe()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.screens = {
            "start": StartScreen(self),
            "new_project": NewProjectScreen(self),
            "editor": EditorScreen(self),
            "save_project": SaveProjectScreen(self),
            "load_project": LoadProjectScreen(self),
            "settings": SettingsScreen(self),
            "help": HelpScreen(self),
        }

        for screen in self.screens.values():
            self.stack.addWidget(screen)

        self.apply_current_styles()
        self.show_screen(self.START_SCREEN)

    def _load_settings_safe(self) -> AppSettings:
        """Load settings, but fall back to defaults if the settings file is damaged."""
        try:
            return self.storage.load_settings()
        except Exception as error:
            LOGGER.warning("Could not load settings. Default settings will be used. Reason: %s", error)
            return AppSettings()

    def _load_current_project_safe(self) -> Project | None:
        """Load the last opened project without blocking application startup on file errors."""
        try:
            return self.storage.load_current_project()
        except Exception as error:
            LOGGER.warning("Could not load current project. Starting without active project. Reason: %s", error)
            return None

    def show_screen(self, name: str) -> None:
        """Switch to a registered application screen."""
        screen = self.screens.get(name)

        if screen is None:
            LOGGER.warning("Unknown screen requested: %s. Falling back to start screen.", name)
            screen = self.screens[self.START_SCREEN]

        screen.refresh()
        self.stack.setCurrentWidget(screen)

    def set_current_project(self, project: Project) -> None:
        """Update active project and persist it as the last opened project."""
        self.current_project = project

        try:
            self.storage.save_current_project(project)
        except Exception as error:
            LOGGER.warning("Could not save current project state. Reason: %s", error)

    def apply_current_styles(self) -> None:
        """Apply stylesheet generated from current application settings."""
        try:
            self.setStyleSheet(build_stylesheet(self.settings))
        except Exception as error:
            LOGGER.warning("Could not apply stylesheet. Reason: %s", error)
            self.setStyleSheet("")

    @staticmethod
    def format_date(value: str | None) -> str:
        """Format ISO date string for display in the UI."""
        if not value:
            return "-"

        try:
            normalized_value = value.replace("Z", "+00:00")
            return datetime.fromisoformat(normalized_value).strftime("%d.%m.%Y")
        except ValueError:
            return value


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Melody Editor")
    app.setOrganizationName("Melody Editor Project")

    window = MainWindow()
    window.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()