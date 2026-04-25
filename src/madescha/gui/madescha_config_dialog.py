from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from madescha.core.config import MadeschaConfig

class MadeschaConfigDialog(QDialog):
    """
    Dialog window for editing MadeschaConfig settings.

    Displays all configuration options and allows the user to modify and save them.
    """

    def __init__(self, config: MadeschaConfig, parent: QWidget | None = None) -> None:
        """
        Initialize the configuration dialog.

        Args:
            config: The MadeschaConfig instance to edit.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self._config = config

        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.setModal(True)

        self._build_ui()
        self._load_values()

    def _build_ui(self) -> None:
        """Constructs the dialog UI layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # --- Parsing Group ---
        parsing_group = QGroupBox("Document Parsing")
        parsing_layout = QFormLayout(parsing_group)
        parsing_layout.setSpacing(8)

        self._auto_parse_checkbox = QCheckBox("Automatically parse opened documents")
        parsing_layout.addRow(self._auto_parse_checkbox)

        main_layout.addWidget(parsing_group)

        # --- Export Group ---
        export_group = QGroupBox("Export")
        export_layout = QFormLayout(export_group)
        export_layout.setSpacing(8)

        # Export root directory
        self._export_dir_edit = QLineEdit()
        self._export_dir_edit.setPlaceholderText("Select export root directory...")

        browse_button = QPushButton("Browse…")
        browse_button.setFixedWidth(80)
        browse_button.clicked.connect(self._browse_export_directory)

        dir_layout = QHBoxLayout()
        dir_layout.setSpacing(6)
        dir_layout.addWidget(self._export_dir_edit)
        dir_layout.addWidget(browse_button)

        export_layout.addRow("Root directory:", dir_layout)

        # Export format
        self._export_format_edit = QLineEdit()
        self._export_format_edit.setPlaceholderText("e.g. ${date}__${author_short}__${title}")
        export_layout.addRow("Filename format:", self._export_format_edit)

        # Format hint
        hint_label = QLabel(
            "Available variables: <code>${date}</code>, "
            "<code>${author_short}</code>, <code>${author}</code>, <code>${title}</code>"
        )
        hint_label.setWordWrap(True)
        hint_font = QFont()
        hint_font.setPointSize(hint_font.pointSize() - 1)
        hint_label.setFont(hint_font)
        hint_label.setStyleSheet("color: gray;")
        export_layout.addRow("", hint_label)

        main_layout.addWidget(export_group)

        # --- Config file path label ---
        config_path_label = QLabel(f"Config file: <code>{self._config.config_file}</code>")
        config_path_label.setWordWrap(True)
        config_path_label.setTextFormat(Qt.TextFormat.RichText)
        small_font = QFont()
        small_font.setPointSize(small_font.pointSize() - 1)
        config_path_label.setFont(small_font)
        config_path_label.setStyleSheet("color: gray;")
        main_layout.addWidget(config_path_label)

        main_layout.addStretch()

        # --- Dialog Buttons ---
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._save_and_accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def _load_values(self) -> None:
        """Loads current config values into the UI widgets."""
        self._auto_parse_checkbox.setChecked(
            self._config.automatically_parse_opened_documents in (True, "True", "true", "1")
        )
        self._export_dir_edit.setText(self._config.export_root_directory)
        self._export_format_edit.setText(self._config.export_format)

    def _browse_export_directory(self) -> None:
        """Opens a directory picker and updates the export directory field."""
        current_dir = self._export_dir_edit.text() or str(Path.home())
        selected_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Export Root Directory",
            current_dir,
            QFileDialog.Option.ShowDirsOnly,
        )
        if selected_dir:
            self._export_dir_edit.setText(selected_dir)

    def _save_and_accept(self) -> None:
        """Saves the current widget values to config and closes the dialog."""
        self._config.automatically_parse_opened_documents = (
            self._auto_parse_checkbox.isChecked()
        )
        self._config.export_root_directory = self._export_dir_edit.text().strip()
        self._config.export_format = self._export_format_edit.text().strip()
        self._config.save()
        self.accept()
