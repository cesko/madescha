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

from madescha.gui.madescha_widgets import (OpenFileWidget, ProcessingWidget, DocumentInfoWidget)

from madescha.core.datatypes import DocumentInfo, Document, AutoProcessingStatus


class MainWindow(QMainWindow):
    """Main window with a two-column layout: PDF viewer on the left, controls on the right."""

    file_selected = Signal(str)
    document_info_updated = Signal(DocumentInfo)
    #auto_processing_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
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
        right_widget.setFixedWidth(260)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        self._open_file_widget = OpenFileWidget()
        self._processing_widget = ProcessingWidget()
        self._document_info_widget = DocumentInfoWidget()

        right_layout.addWidget(self._open_file_widget)
        right_layout.addWidget(self._processing_widget)
        right_layout.addWidget(self._document_info_widget)

        # - connect -
        self._open_file_widget.file_selected.connect(self.file_selected)
        self._document_info_widget.info_updated.connect(self.document_info_updated)


        # # File group
        # file_group = QGroupBox("File")
        # file_layout = QVBoxLayout(file_group)

        # self._open_button = QPushButton("Open PDF…")
        # self._open_button.clicked.connect(self._open_pdf)
        # file_layout.addWidget(self._open_button)

        # self._close_button = QPushButton("Close PDF")
        # self._close_button.clicked.connect(self._close_pdf)
        # file_layout.addWidget(self._close_button)

        # right_layout.addWidget(file_group)

        # # Navigation group
        # nav_group = QGroupBox("Navigation")
        # nav_layout = QVBoxLayout(nav_group)

        # page_row = QHBoxLayout()
        # page_row.addWidget(QLabel("Page:"))
        # self._page_spin = QSpinBox()
        # self._page_spin.setMinimum(1)
        # self._page_spin.valueChanged.connect(self._go_to_page)
        # page_row.addWidget(self._page_spin)
        # self._page_count_label = QLabel("/ 0")
        # page_row.addWidget(self._page_count_label)
        # nav_layout.addLayout(page_row)

        # nav_buttons = QHBoxLayout()
        # self._prev_button = QPushButton("◀ Prev")
        # self._prev_button.clicked.connect(self._prev_page)
        # nav_buttons.addWidget(self._prev_button)

        # self._next_button = QPushButton("Next ▶")
        # self._next_button.clicked.connect(self._next_page)
        # nav_buttons.addWidget(self._next_button)
        # nav_layout.addLayout(nav_buttons)

        # right_layout.addWidget(nav_group)

        # # Zoom group
        # zoom_group = QGroupBox("Zoom")
        # zoom_layout = QVBoxLayout(zoom_group)

        # zoom_row = QHBoxLayout()
        # zoom_row.addWidget(QLabel("Factor:"))
        # self._zoom_spin = QDoubleSpinBox()
        # self._zoom_spin.setRange(0.1, 5.0)
        # self._zoom_spin.setSingleStep(0.1)
        # self._zoom_spin.setValue(1.0)
        # self._zoom_spin.setSuffix("×")
        # self._zoom_spin.valueChanged.connect(self._apply_zoom)
        # zoom_row.addWidget(self._zoom_spin)
        # zoom_layout.addLayout(zoom_row)

        # zoom_buttons = QHBoxLayout()
        # zoom_in_btn = QPushButton("Zoom In")
        # zoom_in_btn.clicked.connect(lambda: self._zoom_step(0.1))
        # zoom_buttons.addWidget(zoom_in_btn)

        # zoom_out_btn = QPushButton("Zoom Out")
        # zoom_out_btn.clicked.connect(lambda: self._zoom_step(-0.1))
        # zoom_buttons.addWidget(zoom_out_btn)
        # zoom_layout.addLayout(zoom_buttons)

        # zoom_fit_btn = QPushButton("Fit to Width")
        # zoom_fit_btn.clicked.connect(self._fit_to_width)
        # zoom_layout.addWidget(zoom_fit_btn)

        # right_layout.addWidget(zoom_group)

        # # Document info group
        # info_group = QGroupBox("Document Info")
        # info_layout = QFormLayout(info_group)
        # self._title_label = QLabel("—")
        # self._title_label.setWordWrap(True)
        # self._author_label = QLabel("—")
        # self._pages_label = QLabel("—")
        # info_layout.addRow("Title:", self._title_label)
        # info_layout.addRow("Author:", self._author_label)
        # info_layout.addRow("Pages:", self._pages_label)
        # right_layout.addWidget(info_group)

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

        # page_count = self._document.pageCount()
        # self._page_spin.setMaximum(max(page_count, 1))
        # self._page_spin.setValue(1)
        # self._page_count_label.setText(f"/ {page_count}")
        # self._pages_label.setText(str(page_count))
        # self._title_label.setText(
        #     self._document.metaData(QPdfDocument.MetaDataField.Title) or "—"
        # )
        # self._author_label.setText(
        #     self._document.metaData(QPdfDocument.MetaDataField.Author) or "—"
        # )
        # self._update_controls()

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
        # self._page_spin.setMaximum(1)
        # self._page_spin.setValue(1)
        # self._page_count_label.setText("/ 0")
        # self._title_label.setText("—")
        # self._author_label.setText("—")
        # self._pages_label.setText("—")
        # self._update_controls()

    # def _go_to_page(self, page_number: int) -> None:
    #     """Navigate the PDF view to *page_number* (1-based)."""
    #     navigator = self._pdf_view.pageNavigator()
    #     navigator.jump(page_number - 1, navigator.currentLocation(), navigator.currentZoom())

    # def _prev_page(self) -> None:
    #     """Go to the previous page."""
    #     self._page_spin.setValue(max(1, self._page_spin.value() - 1))

    # def _next_page(self) -> None:
    #     """Go to the next page."""
    #     self._page_spin.setValue(
    #         min(self._document.pageCount(), self._page_spin.value() + 1)
    #     )

    # def _apply_zoom(self, factor: float) -> None:
    #     """Apply *factor* as the zoom level of the PDF view."""
    #     navigator = self._pdf_view.pageNavigator()
    #     navigator.jump(navigator.currentPage(), navigator.currentLocation(), factor)

    # def _zoom_step(self, delta: float) -> None:
    #     """Increment or decrement zoom by *delta*."""
    #     new_value = round(self._zoom_spin.value() + delta, 2)
    #     self._zoom_spin.setValue(max(0.1, min(5.0, new_value)))

    def _fit_to_width(self) -> None:
        """Set zoom mode to fit the page width."""
        self._pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)

    def _update_controls(self) -> None:
        """Enable or disable controls depending on whether a document is loaded."""
        # loaded = self._document.pageCount() > 0
        # self._close_button.setEnabled(loaded)
        # self._prev_button.setEnabled(loaded)
        # self._next_button.setEnabled(loaded)
        # self._page_spin.setEnabled(loaded)
        # self._zoom_spin.setEnabled(loaded)
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())