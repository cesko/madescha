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
    QFormLayout, QWidget, QSpinBox, QDoubleSpinBox, QSizePolicy, QTextEdit,
    QDialogButtonBox, QDateEdit
)
from PySide6.QtCore import Qt, Signal, Slot, QDate

from madescha.core.datatypes import AutoProcessingStatus, DocumentInfo, Date


class OpenFileWidget(QWidget):
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


class TextDialog(QDialog):
    """Dialog window that displays a long text in a scrollable text area."""

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        """
        Initialize the TextDialog.

        Args:
            text: The long text content to display.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle("Long Text Dialog")
        self.resize(600, 400)
        self._setup_ui(text)

    def _setup_ui(self, text: str) -> None:
        """
        Set up the dialog UI components.

        Args:
            text: The text content to display in the text area.
        """
        layout = QVBoxLayout(self)

        # Scrollable, read-only text area
        text_edit = QTextEdit()
        text_edit.setPlainText(text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)

        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

class ProcessingState(Enum):
    """Enum representing the possible states of the processing widget."""
    NONE = auto()
    PROCESSING = auto()
    FINISHED = auto()
    FAILED = auto()


class ProcessingWidget(QWidget):
    """Widget that displays processing state with action buttons and a status label."""

    apply_fields_clicked = Signal(DocumentInfo)
    start_processing_requested = Signal()
    stop_processing_requested = Signal()

    STATE_SYMBOLS: dict[ProcessingState, str] = {
        ProcessingState.NONE: "",
        ProcessingState.PROCESSING: "⏳",
        ProcessingState.FINISHED: "✅",
        ProcessingState.FAILED: "❌",
    }

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the Processing widget.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self._state: ProcessingState = ProcessingState.NONE
        self._setup_ui()
        self._ocr_text = ""
        self._fields = DocumentInfo()

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
        self._start_button = QPushButton("Start")
        self._stop_button = QPushButton("Stop")
        self._view_text_button = QPushButton("View Text")
        self._apply_fields_button = QPushButton("Apply Fields")
        self._view_text_button.clicked.connect(self._open_ocr_text_dialog)
        self._apply_fields_button.clicked.connect(self.apply_fields)
        self._start_button.clicked.connect(self.start_processing_requested)
        self._stop_button.clicked.connect(self.stop_processing_requested)
        button_layout.addWidget(self._start_button)
        button_layout.addWidget(self._stop_button)
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
    
    def apply_fields(self) -> None:
        self.apply_fields_clicked.emit(self._fields)


    @Slot(AutoProcessingStatus)
    def set_status(self, status:AutoProcessingStatus) -> None:
        if status.running:
            self.set_state(ProcessingState.PROCESSING)
        elif status.success:
            self.set_state(ProcessingState.FINISHED)
        else:
            self.set_state(ProcessingState.FAILED)
        
        self.set_status_text(status.status_message)
        self._ocr_text = status.ocr_text
        self._fields = status.fields

        if status.success:
            self.apply_fields()

    def _open_ocr_text_dialog(self) -> None:
        """Open the text dialog when the button is clicked."""
        dialog = TextDialog(self._ocr_text, parent=self)
        dialog.exec()


class DocumentInfoWidget(QWidget):
    """
    A form widget that displays and edits document metadata.

    Signals
    -------
    info_updated : Signal(DocumentFields)
        Emitted whenever any field value changes.
    """

    info_updated = Signal(DocumentInfo)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._connect_signals()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Create and arrange all child widgets."""
        main_layout = QVBoxLayout(self)
        group_box = QGroupBox("Document Info")
        layout = QFormLayout(group_box)

        self._author_edit = QLineEdit(self)
        self._author_edit.setPlaceholderText("unknown")

        self._author_short_edit = QLineEdit(self)
        self._author_short_edit.setPlaceholderText("unknown")

        self._title_edit = QLineEdit(self)
        self._title_edit.setPlaceholderText("unknown")

        self._date_edit = QDateEdit(self)
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDisplayFormat("yyyy-MM-dd")
        self._date_edit.setDate(QDate(1, 1, 1))  # matches Date() defaults

        layout.addRow("Author", self._author_edit)
        layout.addRow("Author Short", self._author_short_edit)
        layout.addRow("Title", self._title_edit)
        layout.addRow("Date", self._date_edit)

        main_layout.addWidget(group_box)

    def _connect_signals(self) -> None:
        """Wire internal widget signals to the unified change handler."""
        self._author_edit.textChanged.connect(self._on_field_changed)
        self._author_short_edit.textChanged.connect(self._on_field_changed)
        self._title_edit.textChanged.connect(self._on_field_changed)
        self._date_edit.dateChanged.connect(self._on_field_changed)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _current_document(self) -> DocumentInfo:
        """Build a :class:`DocumentFields` snapshot from the current UI state."""
        q_date: QDate = self._date_edit.date()
        return DocumentInfo(
            author=self._author_edit.text() or "unknown",
            author_short=self._author_short_edit.text() or "unknown",
            title=self._title_edit.text() or "unknown",
            date=Date(
                year=q_date.year(),
                month=q_date.month(),
                day=q_date.day(),
            ),
        )

    def _on_field_changed(self, *_args: object) -> None:
        """Emit :attr:`document_changed` whenever any field is edited."""
        self.info_updated.emit(self._current_document())

    # ------------------------------------------------------------------
    # Public slots
    # ------------------------------------------------------------------

    @Slot(DocumentInfo)
    def set_document(self, doc: DocumentInfo) -> None:
        """
        Populate all fields from *doc*.

        Parameters
        ----------
        doc:
            A :class:`DocumentFields` instance whose values will be written
            into the form widgets.
        """
        # Block individual signals so we emit document_changed only once.
        self._author_edit.blockSignals(True)
        self._author_short_edit.blockSignals(True)
        self._title_edit.blockSignals(True)
        self._date_edit.blockSignals(True)

        self._author_edit.setText(doc.author)
        self._author_short_edit.setText(doc.author_short)
        self._title_edit.setText(doc.title)
        self._date_edit.setDate(QDate(doc.date.year, doc.date.month, doc.date.day))

        self._author_edit.blockSignals(False)
        self._author_short_edit.blockSignals(False)
        self._title_edit.blockSignals(False)
        self._date_edit.blockSignals(False)

        self.info_updated.emit(self._current_document())

    @Slot(str)
    def set_author(self, author: str) -> None:
        """
        Update only the *author* field.

        Parameters
        ----------
        author:
            New author string.
        """
        self._author_edit.setText(author)

    @Slot(str)
    def set_title(self, title: str) -> None:
        """
        Update only the *title* field.

        Parameters
        ----------
        title:
            New title string.
        """
        self._title_edit.setText(title)

    @Slot(Date)
    def set_date(self, date: Date) -> None:
        """
        Update only the *date* field.

        Parameters
        ----------
        date:
            A :class:`Date` instance with *year*, *month*, and *day*.
        """
        self._date_edit.setDate(QDate(date.year, date.month, date.day))



class ExportWidget(QWidget):
    """
    Trigger document export.

    Signals
    -------
    export_directory_selected : Signal(str)
        Emitted when the export directory was selected.
    """

    export_directory_selected = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Group box
        group_box = QGroupBox("Export")
        group_layout = QVBoxLayout(group_box)

        # Export button
        self._export_button = QPushButton("Export")
        self._export_button.clicked.connect(self._on_export_clicked)
        group_layout.addWidget(self._export_button)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(group_box)

    def _on_export_clicked(self) -> None:
        """Open a directory selection dialog and emit the selected path."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Export Directory",
        )
        if directory:
            self.export_directory_selected.emit(directory)
        


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    container = QWidget()
    layout = QVBoxLayout(container)  # Set layout on the container

    open_file = OpenFileWidget()
    processing = ProcessingWidget()
    fields = DocumentInfoWidget()

    layout.addWidget(open_file)
    layout.addWidget(processing)
    layout.addWidget(fields)

    processing.apply_fields_clicked.connect(lambda: print("Apply Fields clicked"))

    window = QMainWindow()
    window.setCentralWidget(container)  # Set the container as central widget
    window.show()

    sys.exit(app.exec())