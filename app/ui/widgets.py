from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QFont, QKeyEvent, QMouseEvent, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QAbstractSpinBox, QSpinBox, QStyle, QStyleOptionSpinBox, QWidget

from app.core.models import Note

PITCH_RANGES = {
    "c3-c5": [
        "C5", "B4", "A4", "G4", "F4",
        "E4", "D4", "C4", "B3", "A3",
        "G3", "F3", "E3", "D3", "C3",
    ],
    "c4-c6": [
        "C6", "B5", "A5", "G5", "F5",
        "E5", "D5", "C5", "B4", "A4",
        "G4", "F4", "E4", "D4", "C4",
    ],
    "c5-c7": [
        "C7", "B6", "A6", "G6", "F6",
        "E6", "D6", "C6", "B5", "A5",
        "G5", "F5", "E5", "D5", "C5",
    ],
}

DEFAULT_PITCH_RANGE = "c4-c6"

# Kept for compatibility with older imports.
PITCH_NAMES = PITCH_RANGES[DEFAULT_PITCH_RANGE]




class ReadableSpinBox(QSpinBox):
    """QSpinBox with explicitly painted plus/minus symbols.

    Some Windows/PySide6 style combinations hide the native spinbox
    arrows when QSS is used. This subclass keeps the native clickable
    controls, but draws readable + and − symbols over the button area.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        super().paintEvent(event)

        option = QStyleOptionSpinBox()
        self.initStyleOption(option)

        up_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_SpinBox,
            option,
            QStyle.SubControl.SC_SpinBoxUp,
            self,
        )
        down_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_SpinBox,
            option,
            QStyle.SubControl.SC_SpinBoxDown,
            self,
        )

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = self.palette().color(self.foregroundRole())
        painter.setPen(color)

        font = QFont(self.font())
        font.setBold(True)
        font.setPointSize(max(font.pointSize() + 1, 11))
        painter.setFont(font)

        painter.drawText(up_rect, Qt.AlignmentFlag.AlignCenter, "+")
        painter.drawText(down_rect, Qt.AlignmentFlag.AlignCenter, "−")

class MelodyGridWidget(QWidget):
    notes_changed = Signal()

    def __init__(self) -> None:
        super().__init__()

        self.notes: list[Note] = []
        self.pitch_names = PITCH_RANGES[DEFAULT_PITCH_RANGE]
        self.bars = 8
        self.cell_w = 32
        self.cell_h = 30
        self.left_margin = 54
        self.top_margin = 44
        self.selected_note_id: str | None = None
        self.playback_step = -1
        self.dark_theme = False
        self.keyboard_shortcuts_enabled = True

        self.is_drawing = False
        self.is_erasing = False
        self.last_touched_cell: tuple[int, int] | None = None

        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumSize(1120, 560)

    @property
    def columns(self) -> int:
        return max(4, self.bars * 4)

    @property
    def rows(self) -> int:
        return len(self.pitch_names)

    def set_dark_theme(self, enabled: bool) -> None:
        self.dark_theme = enabled
        self.update()

    def set_keyboard_shortcuts_enabled(self, enabled: bool) -> None:
        self.keyboard_shortcuts_enabled = bool(enabled)

    def set_project_data(
        self,
        notes: list[Note],
        bars: int,
        pitch_range: str = DEFAULT_PITCH_RANGE,
    ) -> None:
        self.pitch_names = PITCH_RANGES.get(
            pitch_range,
            PITCH_RANGES[DEFAULT_PITCH_RANGE],
        )

        self.bars = max(1, bars)
        self.notes = self._sanitize_notes(notes)
        self.playback_step = -1
        self.selected_note_id = None

        self.setMinimumSize(
            self.left_margin + self.columns * self.cell_w + 24,
            self.top_margin + self.rows * self.cell_h + 24,
        )

        self.update()

    def set_playback_step(self, step: int) -> None:
        self.playback_step = step
        self.update()

    def clear_playback(self) -> None:
        self.playback_step = -1
        self.update()

    def note_name_for_pitch(self, pitch: int) -> str | None:
        if 0 <= pitch < len(self.pitch_names):
            return self.pitch_names[pitch]

        return None

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802 - Qt naming convention
        del event

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        colors = self._colors()
        painter.fillRect(self.rect(), QColor(colors["background"]))

        self._draw_headers(painter, colors)
        self._draw_grid(painter, colors)
        self._draw_notes(painter, colors)
        self._draw_playback_line(painter)

    def _draw_headers(self, painter: QPainter, colors: dict[str, str]) -> None:
        painter.setPen(QColor(colors["text_secondary"]))
        painter.setFont(QFont("Segoe UI", 9))

        for row, pitch_name in enumerate(self.pitch_names):
            y = self.top_margin + row * self.cell_h + self.cell_h // 2 + 5
            painter.drawText(8, y, pitch_name)

        for col in range(self.columns):
            if col % 4 == 0:
                bar = col // 4 + 1
                x = self.left_margin + col * self.cell_w
                painter.drawText(
                    QRect(x, 10, self.cell_w * 4, 24),
                    Qt.AlignCenter,
                    str(bar),
                )

    def _draw_grid(self, painter: QPainter, colors: dict[str, str]) -> None:
        grid_rect = QRect(
            self.left_margin,
            self.top_margin,
            self.columns * self.cell_w,
            self.rows * self.cell_h,
        )

        painter.setPen(QPen(QColor(colors["grid_strong"]), 1))
        painter.drawRect(grid_rect)

        for col in range(self.columns + 1):
            x = self.left_margin + col * self.cell_w
            line_color = colors["grid_strong"] if col % 4 == 0 else colors["grid_light"]

            painter.setPen(QPen(QColor(line_color), 1))
            painter.drawLine(
                x,
                self.top_margin,
                x,
                self.top_margin + self.rows * self.cell_h,
            )

        for row in range(self.rows + 1):
            y = self.top_margin + row * self.cell_h

            painter.setPen(QPen(QColor(colors["grid_light"]), 1))
            painter.drawLine(
                self.left_margin,
                y,
                self.left_margin + self.columns * self.cell_w,
                y,
            )

    def _draw_notes(self, painter: QPainter, colors: dict[str, str]) -> None:
        for note in self.notes:
            if not self._is_inside_grid(note.pitch, note.time):
                continue

            rect = self._cell_rect(note.pitch, note.time).adjusted(4, 4, -4, -4)
            selected = note.id == self.selected_note_id

            painter.setBrush(QColor(colors["note_selected"] if selected else colors["note"]))
            painter.setPen(
                QPen(
                    QColor(colors["note_border_selected"] if selected else colors["note_border"]),
                    2 if selected else 1,
                )
            )
            painter.drawRoundedRect(rect, 6, 6)

    def _draw_playback_line(self, painter: QPainter) -> None:
        if self.playback_step < 0:
            return

        x = self.left_margin + min(self.playback_step, self.columns) * self.cell_w

        painter.setPen(QPen(QColor("#ef4444"), 3))
        painter.drawLine(
            x,
            self.top_margin - 4,
            x,
            self.top_margin + self.rows * self.cell_h + 4,
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        self.setFocus()

        cell = self._cell_from_point(event.position().toPoint())
        if cell is None:
            return

        if event.button() == Qt.RightButton:
            self.is_erasing = True
            self.is_drawing = False
            self.last_touched_cell = None
            self._apply_drag_cell(cell, erase=True)
            event.accept()
            return

        if event.button() == Qt.LeftButton:
            self.is_drawing = True
            self.is_erasing = False
            self.last_touched_cell = None
            self._apply_drag_cell(cell, erase=False)
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        cell = self._cell_from_point(event.position().toPoint())
        if cell is None:
            super().mouseMoveEvent(event)
            return

        if self.is_drawing and event.buttons() & Qt.LeftButton:
            self._apply_drag_cell(cell, erase=False)
            event.accept()
            return

        if self.is_erasing and event.buttons() & Qt.RightButton:
            self._apply_drag_cell(cell, erase=True)
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        self.is_drawing = False
        self.is_erasing = False
        self.last_touched_cell = None

        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if not self.keyboard_shortcuts_enabled:
            super().keyPressEvent(event)
            return

        selected = self._selected_note()

        if selected is None:
            super().keyPressEvent(event)
            return

        key = event.key()

        if key == Qt.Key_Delete:
            self._delete_note(selected)
            event.accept()
            return

        move_map = {
            Qt.Key_Left: (0, -1),
            Qt.Key_Right: (0, 1),
            Qt.Key_Up: (-1, 0),
            Qt.Key_Down: (1, 0),
        }

        if key in move_map:
            pitch_delta, time_delta = move_map[key]
            self._move_note(selected, pitch_delta, time_delta)
            event.accept()
            return

        super().keyPressEvent(event)

    def _select_or_create_note(self, note: Note | None, pitch: int, time: int) -> None:
        if note is not None:
            self.selected_note_id = note.id
            self.update()
            return

        new_note = Note.create(pitch=pitch, time=time)
        self.notes.append(new_note)
        self.selected_note_id = new_note.id

        self.notes_changed.emit()
        self.update()

    def _apply_drag_cell(self, cell: tuple[int, int], erase: bool) -> None:
        if self.last_touched_cell == cell:
            return

        pitch, time = cell
        note = self._find_note(pitch, time)

        if erase:
            self._delete_note(note)
        else:
            self._select_or_create_note(note, pitch, time)

        self.last_touched_cell = cell

    def _delete_note(self, note: Note | None) -> None:
        if note is None:
            return

        self.notes.remove(note)

        if self.selected_note_id == note.id:
            self.selected_note_id = None

        self.notes_changed.emit()
        self.update()

    def _move_note(self, note: Note, pitch_delta: int, time_delta: int) -> None:
        new_pitch = min(max(note.pitch + pitch_delta, 0), self.rows - 1)
        new_time = min(max(note.time + time_delta, 0), self.columns - 1)

        if new_pitch == note.pitch and new_time == note.time:
            return

        if not self._is_cell_free(new_pitch, new_time, ignored_note_id=note.id):
            return

        note.pitch = new_pitch
        note.time = new_time

        self.notes_changed.emit()
        self.update()

    def _cell_rect(self, pitch: int, time: int) -> QRect:
        return QRect(
            self.left_margin + time * self.cell_w,
            self.top_margin + pitch * self.cell_h,
            self.cell_w,
            self.cell_h,
        )

    def _cell_from_point(self, point: QPoint) -> tuple[int, int] | None:
        x = point.x() - self.left_margin
        y = point.y() - self.top_margin

        if x < 0 or y < 0:
            return None

        time = x // self.cell_w
        pitch = y // self.cell_h

        if self._is_inside_grid(pitch, time):
            return int(pitch), int(time)

        return None

    def _find_note(self, pitch: int, time: int) -> Note | None:
        for note in self.notes:
            if note.pitch == pitch and note.time == time:
                return note

        return None

    def _selected_note(self) -> Note | None:
        for note in self.notes:
            if note.id == self.selected_note_id:
                return note

        return None

    def _is_cell_free(self, pitch: int, time: int, ignored_note_id: str | None = None) -> bool:
        for note in self.notes:
            if note.id == ignored_note_id:
                continue

            if note.pitch == pitch and note.time == time:
                return False

        return True

    def _is_inside_grid(self, pitch: int, time: int) -> bool:
        return 0 <= pitch < self.rows and 0 <= time < self.columns

    def _sanitize_notes(self, notes: list[Note]) -> list[Note]:
        sanitized_notes: list[Note] = []
        occupied_cells: set[tuple[int, int]] = set()

        for note in notes:
            note.pitch = min(max(note.pitch, 0), self.rows - 1)
            note.time = min(max(note.time, 0), self.columns - 1)

            cell = (note.pitch, note.time)
            if cell in occupied_cells:
                continue

            occupied_cells.add(cell)
            sanitized_notes.append(note)

        return sanitized_notes

    def _colors(self) -> dict[str, str]:
        if self.dark_theme:
            return {
                "background": "#020617",
                "text_secondary": "#cbd5e1",
                "grid_light": "#334155",
                "grid_strong": "#64748b",
                "note": "#3b82f6",
                "note_border": "#60a5fa",
                "note_selected": "#2563eb",
                "note_border_selected": "#f8fafc",
            }

        return {
            "background": "#ffffff",
            "text_secondary": "#475569",
            "grid_light": "#e2e8f0",
            "grid_strong": "#94a3b8",
            "note": "#3b82f6",
            "note_border": "#2563eb",
            "note_selected": "#1d4ed8",
            "note_border_selected": "#0f172a",
        }