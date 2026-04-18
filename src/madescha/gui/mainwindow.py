from __future__ import annotations

import math
import sys

from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtPdf import QPdfDocument
from PySide6.QtWidgets import (
    QApplication, QDialog, QFileDialog, QLabel, QLineEdit, QMainWindow, 
    QMessageBox, QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QFormLayout, QWidget, QSpinBox, QDoubleSpinBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, Slot

from madescha.gui.madescha_widgets import (OpenFileWidget, ProcessingWidget, DocumentInfoWidget, ExportWidget)

from madescha.core.datatypes import DocumentInfo, Document, AutoProcessingStatus
from madescha.core.config import MadeschaConfig


class MainWindow(QMainWindow):
    """Main window with a two-column layout: PDF viewer on the left, controls on the right."""

    file_selected = Signal(str)
    document_info_updated = Signal(DocumentInfo)
    start_auto_processing_requested = Signal()
    stop_auto_processing_requested = Signal()

    def __init__(self, config:MadeschaConfig, parent=None, ):
        super().__init__(parent)
        self._config = config

        self.setWindowTitle("Madescha")
        self.resize(1200, 800)

        self._document = QPdfDocument(self)

        # Central widget and main horizontal layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # ── Left column: PDF viewer ──────────────────────────────────────────
        self._pdf_view = QPdfView(self)
        self._pdf_view.setDocument(self._document)
        self._pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
        self._pdf_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)

        main_layout.addWidget(self._pdf_view, stretch=3)

        # ── Right column: controls ───────────────────────────────────────────
        right_widget = QWidget(self)
        right_widget.setFixedWidth(320)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        self._open_file_widget = OpenFileWidget(self._config)
        self._processing_widget = ProcessingWidget(self._config)
        self._document_info_widget = DocumentInfoWidget(self._config)
        self._export_widget = ExportWidget(self._config)

        right_layout.addWidget(self._open_file_widget)
        right_layout.addWidget(self._processing_widget)
        right_layout.addWidget(self._document_info_widget)
        right_layout.addWidget(self._export_widget)

        # - connect -
        self._open_file_widget.file_selected.connect(self.file_selected)

        self._processing_widget.start_processing_requested.connect(self.start_auto_processing_requested)
        self._processing_widget.stop_processing_requested.connect(self.stop_auto_processing_requested)
        self._processing_widget.apply_fields_clicked.connect(self._document_info_widget.set_document)

        self._document_info_widget.info_updated.connect(self.document_info_updated)

        # Spacer
        right_layout.addStretch()

        main_layout.addWidget(right_widget, stretch=0)

        self._update_controls()

    # ── Slots ────────────────────────────────────────────────────────────────

    def open_pdf(self, path: str) -> None:
        """Load a PDF from *path*, showing an error dialog on failure."""
        result = self._document.load(path)
        if result != QPdfDocument.Error.None_:
            QMessageBox.critical(self, "Error", f"Could not open PDF:\n{path}")
            return

    def set_auto_processing(self, status:AutoProcessingStatus):
        self._processing_widget.set_status(status)
        pass

    def _open_pdf(self) -> None:
        """Open a file dialog to select and load a PDF."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Open PDF", "", "PDF Files (*.pdf);;All Files (*)"
        )
        if path:
            self.open_pdf(path)

    def _close_pdf(self) -> None:
        """Close the currently loaded PDF document."""
        self._document.close()
       
    def _fit_to_width(self) -> None:
        """Set zoom mode to fit the page width."""
        self._pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)

    def _update_controls(self) -> None:
        """Enable or disable controls depending on whether a document is loaded."""
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())