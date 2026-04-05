from enum import Enum, auto


from PySide6.QtWidgets import (
    QApplication, QDialog, QFileDialog, QLabel, QLineEdit, QMainWindow, 
    QMessageBox, QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QFormLayout, QWidget, QSpinBox, QDoubleSpinBox, QSizePolicy
)
from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QApplication, QDialog, QFileDialog, QLabel, QLineEdit, QMainWindow, 
    QMessageBox, QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QFormLayout, QWidget, QSpinBox, QDoubleSpinBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, Slot

from madescha.madescha_types import AutoProcessingStatus


class OpenFile(QWidget):
    """Widget that provides a file selection dialog through a button click."""
    
    file_selected = Signal(str)
    
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the OpenFile widget.
        
        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the user interface components."""
        main_layout = QVBoxLayout(self)
        
        group_box = QGroupBox("File Selection")
        group_layout = QVBoxLayout(group_box)
        
        self._open_button = QPushButton("Open File")
        self._open_button.clicked.connect(self._on_open_file)
        group_layout.addWidget(self._open_button)
        
        main_layout.addWidget(group_box)
    
    def _on_open_file(self) -> None:
        """Handle the open file button click and emit the selected file path."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a File",
            "",
            "All Files (*)"
        )
        
        if file_path:
            self.file_selected.emit(file_path)


class ProcessingState(Enum):
    """Enum representing the possible states of the processing widget."""
    PROCESSING = auto()
    FINISHED = auto()
    FAILED = auto()


class Processing(QWidget):
    """Widget that displays processing state with action buttons and a status label."""

    view_text_clicked = Signal()
    apply_fields_clicked = Signal()

    STATE_SYMBOLS: dict[ProcessingState, str] = {
        ProcessingState.LOADING: "⏳",
        ProcessingState.FINISHED: "✅",
        ProcessingState.FAILED: "❌",
    }

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the Processing widget.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self._state: ProcessingState = ProcessingState.LOADING
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface components."""
        main_layout = QVBoxLayout(self)

        group_box = QGroupBox("Processing")
        group_layout = QVBoxLayout(group_box)

        # Top row: status symbol on the left, buttons on the right
        top_row_layout = QHBoxLayout()

        self._state_symbol_label = QLabel()
        self._state_symbol_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._state_symbol_label.setStyleSheet("font-size: 24px;")
        self._state_symbol_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        top_row_layout.addWidget(self._state_symbol_label)

        top_row_layout.addStretch()

        button_layout = QVBoxLayout()
        self._view_text_button = QPushButton("View Text")
        self._apply_fields_button = QPushButton("Apply Fields")
        self._view_text_button.clicked.connect(self.view_text_clicked)
        self._apply_fields_button.clicked.connect(self.apply_fields_clicked)
        button_layout.addWidget(self._view_text_button)
        button_layout.addWidget(self._apply_fields_button)
        top_row_layout.addLayout(button_layout)

        group_layout.addLayout(top_row_layout)

        # Status label underneath
        self._status_label = QLabel()
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        group_layout.addWidget(self._status_label)

        main_layout.addWidget(group_box)

        self._update_ui()

    def _update_ui(self) -> None:
        """Update UI elements to reflect the current state."""
        self._state_symbol_label.setText(self.STATE_SYMBOLS[self._state])
        self._status_label.setText(self.STATE_LABELS[self._state])


    def set_state(self, state: ProcessingState) -> None:
        """Set the current processing state and update the UI.

        Args:
            state: The new processing state.
        """
        self._state = state
        self._update_ui()

    def get_state(self) -> ProcessingState:
        """Get the current processing state.

        Returns:
            The current ProcessingState.
        """
        return self._state

    def set_status_text(self, text: str) -> None:
        """Override the status label text manually.

        Args:
            text: The status message to display.
        """
        self._status_label.setText(text)

    @Slot(AutoProcessingStatus)
    def set_status(status:AutoProcessingStatus) -> None:
        pass


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    widget = Processing()
    widget.view_text_clicked.connect(lambda: print("View Text clicked"))
    widget.apply_fields_clicked.connect(lambda: print("Apply Fields clicked"))
    widget.show()

    sys.exit(app.exec())