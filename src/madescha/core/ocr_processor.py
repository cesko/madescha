import os
import tempfile
import shutil
from pathlib import Path

import ocrmypdf
import fitz  # PyMuPDF


class OcrProcessor:
    """
    A class to handle OCR processing of PDF documents using ocrmypdf and PyMuPDF.
    """

    def __init__(self):
        """Initialize the OcrProcessor with no document loaded."""
        self._original_document: str | None = None
        self._processed_document_temp: str | None = None

    def open_document(self, path: str) -> None:
        """
        Open a PDF document for OCR processing.

        Args:
            path: The file path to the PDF document.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file is not a PDF.
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if path.suffix.lower() != ".pdf":
            raise ValueError(f"File must be a PDF: {path}")

        self._original_document = str(path)
        # Reset any previously processed document
        self._cleanup_temp()
        self._processed_document_temp = None

    def run(self) -> None:
        """
        Run OCR on the original document.
        This creates a new temporary document with the text layer.
        When OCR was already present, the temporary one is the old one.

        Raises:
            RuntimeError: If no document has been opened.
        """
        if self._original_document is None:
            raise RuntimeError("No document opened. Call open_document() first.")

        # Create a temporary file for the processed document
        temp_file = tempfile.NamedTemporaryFile(
            suffix=".pdf", delete=False, prefix="ocr_processed_"
        )
        temp_path = temp_file.name
        temp_file.close()

        try:
            exit_code = ocrmypdf.ocr(
                input_file_or_options=self._original_document,
                output_file=temp_path,
                mode="skip",      # replaces deprecated skip_text=True
                deskew=True,
                language=["eng"],
                oversample=300,
            )
            self._cleanup_temp()
            self._processed_document_temp = temp_path

        except ocrmypdf.exceptions.PriorOcrFoundError:
            # If OCR already exists, use the original document as the "processed" one
            self._cleanup_temp()
            shutil.copy2(self._original_document, temp_path)
            self._processed_document_temp = temp_path

        except Exception as e:
            # Clean up the temp file if something went wrong
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise RuntimeError(f"OCR processing failed: {e}") from e

    def export(self, path: str) -> None:
        """
        Export the processed document to the specified path.

        Args:
            path: The destination file path for the processed document.

        Raises:
            RuntimeError: If OCR has not been run yet.
        """
        if self._processed_document_temp is None:
            raise RuntimeError("No processed document available. Call run() first.")

        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self._processed_document_temp, str(destination))

    def get_text(self) -> str:
        """
        Return the text detected with OCR from the processed document.

        Returns:
            A string containing all extracted text from the document.

        Raises:
            RuntimeError: If OCR has not been run yet.
        """
        if self._processed_document_temp is None:
            raise RuntimeError("No processed document available. Call run() first.")

        text_parts: list[str] = []

        with fitz.open(self._processed_document_temp) as doc:
            for page_num, page in enumerate(doc, start=1):
                page_text = page.get_text("text")
                if page_text.strip():
                    text_parts.append(f"--- Page {page_num} ---\n{page_text}")

        return "\n".join(text_parts)

    def _cleanup_temp(self) -> None:
        """Remove the temporary processed document if it exists."""
        if self._processed_document_temp and os.path.exists(
            self._processed_document_temp
        ):
            os.remove(self._processed_document_temp)
            self._processed_document_temp = None

    def __del__(self):
        """Cleanup temporary files when the object is destroyed."""
        self._cleanup_temp()

    def __repr__(self) -> str:
        return (
            f"OcrProcessor("
            f"document={self._original_document!r}, "
            f"processed={self._processed_document_temp is not None})"
        )
