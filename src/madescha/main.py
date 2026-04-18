import sys
import os
import argparse
import threading
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread
from PySide6.QtCore import QObject, Signal

from madescha.gui.mainwindow import MainWindow
from madescha.core.datatypes import DocumentInfo, Date, AutoProcessingStatus, OcrResult, LlmResult, Document
from madescha.core.ocr_processor import OcrProcessor
from madescha.core.ollama_doc_parser import OllamaDocumentParser
from madescha.utils.utils import organisation_short_name

from caseconverter import snakecase


class MadeschaConfig():
    automatically_parse_opened_documents = True


class AutoProcessingWorker(QObject):
    """
    Worker that runs the OCR + LLM auto processing pipeline in a separate thread.
    Can be cancelled between pipeline stages.
    """
    status_changed = Signal(AutoProcessingStatus)
    finished = Signal()
    llm_parsing_result = Signal(Document)

    def __init__(
        self,
        ocr_processor: OcrProcessor,
        llm_parser: OllamaDocumentParser,
        document_path: str,
    ):
        """
        Args:
            ocr_processor: The OCR processor instance.
            llm_parser: The LLM document parser instance.
            document_path: Path to the document to process.
        """
        super().__init__()
        self._ocr_processor = ocr_processor
        self._llm_parser = llm_parser
        self._document_path = document_path
        self._cancel_event = threading.Event()

    def cancel(self) -> None:
        """Request cancellation of the processing pipeline."""
        self._cancel_event.set()

    @property
    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        return self._cancel_event.is_set()

    def run(self) -> None:
        """
        Execute the auto processing pipeline (OCR -> LLM).
        Checks for cancellation between stages.
        Connected to QThread.started signal.
        """
        status = AutoProcessingStatus(running=True, success=False, status_message="Running OCR...")
        self.status_changed.emit(status)

        # --- OCR Stage ---
        if self.is_cancelled:
            self._emit_cancelled(status)
            self.finished.emit()
            return

        self._ocr_processor.open_document(self._document_path)
        try:
            self._ocr_processor.run()
            ocr_text = self._ocr_processor.get_text()
            ocr_success = True
            ocr_message = "OCR done. Running LLM..."
        except Exception as e:
            ocr_success = False
            ocr_message = str(e)
            ocr_text = ""

        if not ocr_success:
            status.running = False
            status.success = False
            status.status_message = ocr_message
            self.status_changed.emit(status)
            print(status.status_message)
            self.finished.emit()
            return

        status.status_message = ocr_message
        status.ocr_text = ocr_text
        self.status_changed.emit(status)
        print(status.status_message)
        print(status.ocr_text)

        # --- LLM Stage ---
        if self.is_cancelled:
            self._emit_cancelled(status)
            self.finished.emit()
            return

        if not ocr_text:
            status.running = False
            status.success = False
            status.status_message = "Empty OCR result. Skipping LLM."
            self.status_changed.emit(status)
            print(status.status_message)
            self.finished.emit()
            return

        try:
            doc = self._llm_parser.get_document_info(ocr_text)
            self.llm_parsing_result.emit(doc)
            print(f"LLM Parsed Data: {doc}")
            doc_info = DocumentInfo.fromDocument(doc)
            llm_success = True
            llm_message = "LLM parsing done."
        except Exception as e:
            doc_info = DocumentInfo()
            llm_success = False
            llm_message = str(e)

        status.running = False
        status.success = llm_success
        status.status_message = llm_message
        status.fields = doc_info
        self.status_changed.emit(status)
        print(status.status_message)
        print(status.fields)
        self.finished.emit()

    def _emit_cancelled(self, status: AutoProcessingStatus) -> None:
        """
        Emit a cancellation status update.

        Args:
            status: The current status object to update and emit.
        """
        status.running = False
        status.success = False
        status.status_message = "Processing cancelled."
        self.status_changed.emit(status)


class Madescha(QObject):
    """
    The Madescha Logic and Processing Pipeline.
    Independent of GUI but uses Qt Signals and Slots as API.
    """
    pdf_loaded = Signal(str)
    pdf_load_failed = Signal(str)
    auto_processing_status_changed = Signal(AutoProcessingStatus)

    def __init__(self):
        super().__init__()
        self._config = MadeschaConfig()
        self._document_path: str | None = None
        self._ocr_processor = OcrProcessor()
        self._llm_parser = OllamaDocumentParser()

        # Keep strong references to prevent premature GC
        self._worker: AutoProcessingWorker | None = None
        self._worker_thread: QThread | None = None

        self._doc_info = None
        self._doc: Document | None = None

    def open_document(self, path: str) -> None:
        """
        Open a document and optionally trigger auto processing.

        Args:
            path: Path to the PDF document.
        """
        if os.path.exists(path):
            self._document_path = path
            self.pdf_loaded.emit(self._document_path)
        else:
            self.pdf_load_failed.emit(f"File not found: {path}")
            return

        if self._config.automatically_parse_opened_documents:
            self.start_auto_processing()

    def close_document(self) -> None:
        """Close the current document and stop any active processing."""
        self.stop_auto_processing()
        self._document_path = None

    def run_ocr(self) -> OcrResult:
        """
        Run OCR on the currently loaded document.

        Returns:
            OcrResult with success status, message, and extracted text.
        """
        result = OcrResult()
        self._ocr_processor.open_document(self._document_path)
        try:
            self._ocr_processor.run()
            result.success = True
            result.message = "OCR done"
            result.text = self._ocr_processor.get_text()
        except Exception as e:
            result.success = False
            result.message = str(e)
        return result

    def run_llm(self, content: str | None = None) -> LlmResult:
        """
        Run LLM parsing on the given content or last OCR result.

        Args:
            content: Text to parse. Uses last OCR result if None.

        Returns:
            LlmResult with document info, success status, and message.
        """
        if content is None:
            content = self._ocr_processor.get_text()
        if not content:
            return LlmResult(
                DocumentInfo(), False,
                "Empty string provided! Maybe OCR did not produce anything?"
            )

        try:
            doc = self._llm_parser.get_document_info(content)
            return LlmResult(doc, True, "LLM parsing done")
        except Exception as e:
            return LlmResult(DocumentInfo(), False, str(e))

    def start_auto_processing(self) -> None:
        """
        Start the auto processing pipeline (OCR + LLM) in a separate thread.
        If processing is already running, it will be stopped first.
        """
        if not self._document_path:
            return

        # Stop any existing processing before starting new
        self.stop_auto_processing()

        # Create thread first, worker second — never parent worker to Madescha
        worker_thread = QThread()  # No parent: we manage lifetime manually
        worker = AutoProcessingWorker(
            ocr_processor=self._ocr_processor,
            llm_parser=self._llm_parser,
            document_path=self._document_path,
        )

        # Move worker to its thread BEFORE connecting signals
        worker.moveToThread(worker_thread)

        # Wire up signals
        worker_thread.started.connect(worker.run)
        worker.status_changed.connect(self._set_processing_status)
        worker.llm_parsing_result.connect(self.set_llm_parsing_result)

        # Cleanup chain: worker done -> quit thread -> cleanup refs
        worker.finished.connect(worker_thread.quit)
        worker_thread.finished.connect(self._on_worker_thread_finished)

        # Store strong references BEFORE starting
        self._worker = worker
        self._worker_thread = worker_thread

        worker_thread.start()

    def _set_processing_status(self, status: AutoProcessingStatus) -> None:
        """
        Update internal doc info and forward status signal.

        Args:
            status: The current processing status.
        """
        self._doc_info = status.fields
        self.auto_processing_status_changed.emit(status)

    def set_llm_parsing_result(self, doc: Document) -> None:
        """
        Store the LLM parsed document result.

        Args:
            doc: The parsed Document object.
        """
        self._doc = doc

    def stop_auto_processing(self) -> None:
        """
        Request cancellation of the currently running auto processing pipeline
        and wait for the thread to finish.
        """
        if self._worker is not None:
            self._worker.cancel()

        if self._worker_thread is not None and self._worker_thread.isRunning():
            self._worker_thread.quit()
            self._worker_thread.wait()

        # Eagerly clean up so _on_worker_thread_finished doesn't double-clean
        self._cleanup_worker()

    def _on_worker_thread_finished(self) -> None:
        """Clean up worker and thread references after processing completes."""
        self._cleanup_worker()

    def _cleanup_worker(self) -> None:
        """
        Safely delete worker and thread objects and clear references.
        Must only be called after the thread has stopped.
        """
        if self._worker is not None:
            self._worker.deleteLater()
            self._worker = None

        if self._worker_thread is not None:
            self._worker_thread.deleteLater()
            self._worker_thread = None

    def get_export_filename(self) -> str | None:
        """
        Generate an export filename based on parsed document metadata.

        Returns:
            Formatted filename string, or None if no doc info available.
        """
        if self._doc_info:
            date = str(self._doc_info.date)
            author = snakecase(self._doc_info.author)
            title = snakecase(self._doc_info.title)
            if self._doc:
                author = snakecase(organisation_short_name(self._doc.sender))
            return f"{author}__{title}__{date}"
        return None

    def export(self, directory: str) -> None:
        """
        Export the current document to the given directory.

        Args:
            directory: Target directory path.
        """
        filename = self.get_export_filename()
        if filename is None:
            print("Cannot export: no document info available.")
            return
        path = os.path.join(directory, filename)
        print(f"export to {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Madescha - Mach deine Scheiß Ablage!\n"
                    "A little tool to help sort important documents."
    )
    parser.add_argument("file", nargs="?", help="PDF file to open.")
    parser.add_argument(
        "--cli", action="store_true",
        help="Run in command-line mode instead of GUI mode."
    )
    args = parser.parse_args()

    if args.cli:
        cli(args.file)
    else:
        gui(args.file)


def cli(file: str | None = None) -> None:
    """
    Run Madescha in command-line mode.

    Args:
        file: Optional path to a PDF file.
    """
    if file:
        print(f"Opening PDF: {file}")
        print("Not implemented")
    else:
        print("No file specified.")


def gui(file: str | None = None) -> None:
    """
    Run Madescha in GUI mode.

    Args:
        file: Optional path to a PDF file to open on startup.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("Madescha")
    app.setApplicationVersion("0.0.1")

    # Madescha stays on the main thread — no need to move it
    madescha = Madescha()

    window = MainWindow()

    window.file_selected.connect(madescha.open_document)
    madescha.pdf_loaded.connect(window.open_pdf)
    madescha.auto_processing_status_changed.connect(window.set_auto_processing)
    window._export_widget.export_directory_selected.connect(madescha.export)

    # Ensure any running worker is stopped cleanly when the app exits
    app.aboutToQuit.connect(madescha.stop_auto_processing)

    window.show()

    if file:
        madescha.open_document(file)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
