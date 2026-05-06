from __future__ import annotations

from app.core.models import AppSettings


BASE_QSS = """
QMainWindow, QWidget#appRoot {
    background: #f8fafc;
    color: #1e293b;
    font-family: Segoe UI, Arial, sans-serif;
    font-size: 14px;
}

/* Containers */
QFrame#card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}

QFrame#toolbar {
    background: #ffffff;
    border-bottom: 1px solid #cbd5e1;
}

QFrame#statusBar {
    background: #f1f5f9;
    border-top: 1px solid #cbd5e1;
}

/* Text */
QLabel {
    color: #1e293b;
}

QLabel#title {
    color: #1e293b;
    font-size: 32px;
    font-weight: 700;
}

QLabel#subtitle {
    color: #64748b;
    font-size: 15px;
}

QLabel#sectionTitle {
    color: #1e293b;
    font-size: 17px;
    font-weight: 600;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 8px;
}

QLabel#fieldLabel {
    color: #1e293b;
    font-weight: 600;
}

QLabel#detailsBody {
    color: #334155;
    font-size: 15px;
    line-height: 150%;
}

/* Buttons */
QPushButton {
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    padding: 9px 14px;
    background: #ffffff;
    color: #334155;
    min-height: 22px;
}

QPushButton:hover {
    background: #f1f5f9;
}

QPushButton:disabled {
    color: #64748b;
    background: #e2e8f0;
    border-color: #cbd5e1;
}

QPushButton#primaryButton {
    background: #2563eb;
    color: #ffffff;
    border-color: #2563eb;
    font-weight: 600;
}

QPushButton#primaryButton:hover {
    background: #1d4ed8;
}

QPushButton#playButton {
    background: #16a34a;
    color: #ffffff;
    border-color: #16a34a;
    font-weight: 600;
}

QPushButton#playButton:hover {
    background: #15803d;
}

QPushButton#dangerButton {
    color: #dc2626;
    border-color: #fecaca;
    background: #ffffff;
}

QPushButton#dangerButton:hover {
    background: #fef2f2;
}

/* Inputs */
QLineEdit, QSpinBox, QComboBox {
    min-height: 38px;
    background: #f1f5f9;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    padding: 4px 10px;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
    placeholder-text-color: #64748b;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #2563eb;
    background: #ffffff;
    color: #1e293b;
}

QLineEdit:disabled, QSpinBox:disabled, QComboBox:disabled {
    background: #e2e8f0;
    color: #475569;
    border-color: #cbd5e1;
}

QLineEdit:read-only {
    background: #f1f5f9;
    color: #1e293b;
}

/* ComboBox */
QComboBox::drop-down {
    width: 28px;
    border-left: 1px solid #cbd5e1;
    border-top-right-radius: 7px;
    border-bottom-right-radius: 7px;
    background: #e2e8f0;
}

QComboBox::down-arrow {
    width: 0;
    height: 0;
}

QComboBox QAbstractItemView {
    background: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    selection-background-color: #dbeafe;
    selection-color: #1e293b;
    outline: 0;
}

/* Lists and text areas */
QListWidget, QTextEdit {
    background: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
}

QListWidget::item {
    color: #1e293b;
    padding: 10px;
    border-bottom: 1px solid #e2e8f0;
}

QListWidget::item:selected {
    background: #dbeafe;
    color: #1e293b;
    border-left: 4px solid #2563eb;
}

/* Slider */
QSlider::groove:horizontal {
    border: 0;
    height: 6px;
    background: #e2e8f0;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #0f172a;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #ffffff;
    border: 1px solid #64748b;
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

/* Checkboxes */
QCheckBox {
    color: #1e293b;
    spacing: 10px;
}

QCheckBox:disabled {
    color: #64748b;
}
"""


BLACK_QSS = """
QMainWindow, QWidget#appRoot {
    background: #020617;
    color: #e2e8f0;
}

/* Containers */
QFrame#card {
    background: #0f172a;
    border-color: #334155;
}

QFrame#toolbar {
    background: #0f172a;
    border-bottom-color: #334155;
}

QFrame#statusBar {
    background: #111827;
    border-top-color: #334155;
}

/* Text */
QLabel {
    color: #e2e8f0;
}

QLabel#title,
QLabel#sectionTitle,
QLabel#fieldLabel {
    color: #f8fafc;
}

QLabel#subtitle {
    color: #cbd5e1;
}

QLabel#sectionTitle {
    border-bottom-color: #334155;
}

QLabel#detailsBody {
    color: #e2e8f0;
}

/* Buttons */
QPushButton {
    background: #1e293b;
    color: #e2e8f0;
    border-color: #475569;
}

QPushButton:hover {
    background: #334155;
}

QPushButton:disabled {
    background: #0f172a;
    color: #64748b;
    border-color: #334155;
}

QPushButton#primaryButton {
    background: #2563eb;
    color: #ffffff;
    border-color: #2563eb;
}

QPushButton#primaryButton:hover {
    background: #1d4ed8;
}

QPushButton#playButton {
    background: #16a34a;
    color: #ffffff;
    border-color: #16a34a;
}

QPushButton#playButton:hover {
    background: #15803d;
}

QPushButton#dangerButton {
    color: #fca5a5;
    border-color: #7f1d1d;
    background: #1e293b;
}

QPushButton#dangerButton:hover {
    background: #450a0a;
}

/* Inputs */
QLineEdit, QSpinBox, QComboBox {
    background: #020617;
    color: #f8fafc;
    border-color: #475569;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
    placeholder-text-color: #94a3b8;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    background: #0f172a;
    color: #f8fafc;
    border-color: #60a5fa;
}

QLineEdit:disabled, QSpinBox:disabled, QComboBox:disabled {
    background: #1e293b;
    color: #cbd5e1;
    border-color: #475569;
}

QLineEdit:read-only {
    background: #020617;
    color: #f8fafc;
}

/* ComboBox */
QComboBox::drop-down {
    background: #1e293b;
    border-left-color: #475569;
}

QComboBox QAbstractItemView {
    background: #020617;
    color: #f8fafc;
    border-color: #475569;
    selection-background-color: #1d4ed8;
    selection-color: #ffffff;
    outline: 0;
}

/* Lists and text areas */
QListWidget, QTextEdit {
    background: #020617;
    color: #f8fafc;
    border-color: #475569;
}

QListWidget::item {
    color: #f8fafc;
    border-bottom-color: #334155;
}

QListWidget::item:selected {
    background: #1e3a8a;
    color: #ffffff;
    border-left: 4px solid #60a5fa;
}

/* Slider */
QSlider::groove:horizontal {
    background: #334155;
}

QSlider::sub-page:horizontal {
    background: #60a5fa;
}

QSlider::handle:horizontal {
    background: #f8fafc;
    border-color: #60a5fa;
}

/* Checkboxes */
QCheckBox {
    color: #e2e8f0;
}

QCheckBox:disabled {
    color: #64748b;
}
"""


HIGH_CONTRAST_QSS = """
QMainWindow, QWidget#appRoot {
    background: #ffffff;
    color: #000000;
}

QFrame#card,
QFrame#toolbar,
QFrame#statusBar {
    background: #ffffff;
    border: 2px solid #000000;
}

QLabel,
QLabel#title,
QLabel#subtitle,
QLabel#sectionTitle,
QLabel#fieldLabel,
QLabel#detailsBody {
    color: #000000;
}

QPushButton {
    border: 2px solid #000000;
    color: #000000;
    background: #ffffff;
    font-weight: 700;
}

QPushButton:hover {
    background: #eeeeee;
}

QPushButton#primaryButton,
QPushButton#playButton {
    background: #0000ff;
    color: #ffffff;
    border-color: #000000;
}

QPushButton#dangerButton {
    color: #000000;
    background: #ffffff;
    border-color: #000000;
}

QLineEdit,
QSpinBox,
QComboBox,
QListWidget,
QTextEdit {
    background: #ffffff;
    color: #000000;
    border: 2px solid #000000;
    placeholder-text-color: #333333;
}

QComboBox QAbstractItemView {
    background: #ffffff;
    color: #000000;
    selection-background-color: #0000ff;
    selection-color: #ffffff;
}

QListWidget::item:selected {
    background: #0000ff;
    color: #ffffff;
    border-left: 4px solid #000000;
}

QCheckBox {
    color: #000000;
}

QSlider::groove:horizontal {
    background: #000000;
}

QSlider::sub-page:horizontal {
    background: #0000ff;
}

QSlider::handle:horizontal {
    background: #ffffff;
    border: 2px solid #000000;
}
"""


LARGE_TEXT_QSS = """
QWidget {
    font-size: 17px;
}

QLabel#title {
    font-size: 38px;
}

QLabel#subtitle {
    font-size: 18px;
}

QLabel#sectionTitle {
    font-size: 20px;
}
"""


def build_stylesheet(settings: AppSettings) -> str:
    theme = settings.theme.lower().strip()

    sheet = BASE_QSS

    if theme in {"black", "dark"}:
        sheet += BLACK_QSS

    if settings.high_contrast:
        sheet += HIGH_CONTRAST_QSS

    if settings.large_text:
        sheet += LARGE_TEXT_QSS

    return sheet