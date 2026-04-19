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

    delete_original_file_requested = Signal()

    def __init__(self, config:MadeschaConfig, parent=None, ):
        super().__init__(parent)
        self._config = config

        self.setWindowTitle("Madescha")
        self.resize(1200, 800)

        self._document_path = None
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

    def reset(self):
        pass

    # ── Slots ────────────────────────────────────────────────────────────────

    def open_pdf(self, path: str) -> None:
        """Load a PDF from *path*, showing an error dialog on failure."""
        self._document_path = path
        result = self._document.load(path)
        if result != QPdfDocument.Error.None_:
            QMessageBox.critical(self, "Error", f"Could not open PDF:\n{path}")
            return
        
        self._open_file_widget.set_current_file(path)

    def set_auto_processing(self, status:AutoProcessingStatus):
        self._processing_widget.set_status(status)
        pass

    def post_export_dialog(self, export_path: str) -> None:
        """Open dialog to tell the file has been exported and request further action"""

        dialog = QDialog(self)
        dialog.setWindowTitle("Export Successful")
        dialog.setModal(True)
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Message label
        message_label = QLabel(f"File has been successfully exported to:\n{export_path}")
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(message_label)

        # Question label
        action_label = QLabel("Would you like to delete the original file?")
        action_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(action_label)

        layout.addSpacing(8)

        # Buttons layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addStretch()

        # Delete button
        delete_button = QPushButton("Delete")
        delete_button.setToolTip("Delete the original file")
        delete_button.setMinimumWidth(90)
        button_layout.addWidget(delete_button)

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setToolTip("Leave the origninal file in place")
        cancel_button.setMinimumWidth(90)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        # Button actions
        def on_delete() -> None:
            self.delete_original_file_requested.emit()
            dialog.accept()

        def on_cancel() -> None:
            dialog.reject()

        delete_button.clicked.connect(on_delete)
        cancel_button.clicked.connect(on_cancel)

        # Set Cancel as default/escape button
        cancel_button.setDefault(True)
        dialog.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, True)

        result = dialog.exec()
        #if result == QDialog.DialogCode.Accepted:


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
        self._document_path = None
        self._open_file_widget.reset()
        self._processing_widget.reset()
        self._document_info_widget.reset()
        self._export_widget.reset()
       
    def _fit_to_width(self) -> None:
        """Set zoom mode to fit the page width."""
        self._pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)

    def _update_controls(self) -> None:
        """Enable or disable controls depending on whether a document is loaded."""
        pass


    def display_error(self, msg: str) -> None:
        """Display an Error Message Box with the error"""
        error_box = QMessageBox(self)
        error_box.setIcon(QMessageBox.Icon.Critical)
        error_box.setWindowTitle("Error")
        error_box.setText(msg)
        error_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_box.exec()


    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())