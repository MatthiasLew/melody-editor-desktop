from __future__ import annotations

import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from app.core.models import AppSettings, Project


LOGGER = logging.getLogger(__name__)


class Storage:
    """Local JSON storage used as a lightweight replacement for backend persistence."""

    def __init__(self) -> None:
        if getattr(sys, "frozen", False):
            self.root_dir = Path(sys.executable).resolve().parent
        else:
            self.root_dir = Path(__file__).resolve().parents[2]
        self.data_dir = self.root_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.current_project_path = self.data_dir / "current_project.json"
        self.saved_projects_path = self.data_dir / "saved_projects.json"
        self.settings_path = self.data_dir / "settings.json"

    def load_current_project(self) -> Project | None:
        data = self._read_json(self.current_project_path, default=None)

        if not isinstance(data, dict):
            return None

        return Project.from_dict(data)

    def save_current_project(self, project: Project) -> None:
        self._write_json(self.current_project_path, project.to_dict())

    def clear_current_project(self) -> None:
        try:
            self.current_project_path.unlink(missing_ok=True)
        except OSError as error:
            LOGGER.warning("Could not remove current project file. Reason: %s", error)

    def load_saved_projects(self) -> list[Project]:
        data = self._read_json(self.saved_projects_path, default=[])

        if not isinstance(data, list):
            return []

        projects: list[Project] = []

        for item in data:
            if isinstance(item, dict):
                projects.append(Project.from_dict(item))

        return projects

    def save_project_to_library(self, project: Project) -> list[Project]:
        project.saved_at = self._now_iso()

        projects = self.load_saved_projects()
        projects = self._replace_or_insert_project(projects, project)

        self._write_json(
            self.saved_projects_path,
            [item.to_dict() for item in projects],
        )

        self.save_current_project(project)
        return projects

    def delete_project(self, project_name: str) -> list[Project]:
        projects = self.load_saved_projects()
        filtered_projects = [
            project for project in projects
            if project.name != project_name
        ]

        self._write_json(
            self.saved_projects_path,
            [item.to_dict() for item in filtered_projects],
        )

        current_project = self.load_current_project()
        if current_project is not None and current_project.name == project_name:
            self.clear_current_project()

        return filtered_projects

    def load_settings(self) -> AppSettings:
        data = self._read_json(self.settings_path, default={})

        if not isinstance(data, dict):
            return AppSettings()

        return AppSettings.from_dict(data)

    def save_settings(self, settings: AppSettings) -> None:
        self._write_json(self.settings_path, settings.to_dict())

    def _replace_or_insert_project(self, projects: list[Project], project: Project) -> list[Project]:
        for index, existing_project in enumerate(projects):
            if existing_project.name == project.name:
                projects[index] = project
                return projects

        projects.insert(0, project)
        return projects

    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default

        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            LOGGER.warning("Invalid JSON file: %s. Reason: %s", path, error)
            return default
        except OSError as error:
            LOGGER.warning("Could not read JSON file: %s. Reason: %s", path, error)
            return default

    def _write_json(self, path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

        temporary_path = path.with_suffix(f"{path.suffix}.tmp")
        serialized_data = json.dumps(data, indent=2, ensure_ascii=False)

        try:
            temporary_path.write_text(serialized_data, encoding="utf-8")
            temporary_path.replace(path)
        except OSError as error:
            LOGGER.warning("Could not write JSON file: %s. Reason: %s", path, error)
            raise

    @staticmethod
    def _now_iso() -> str:
        return datetime.now().isoformat(timespec="seconds")