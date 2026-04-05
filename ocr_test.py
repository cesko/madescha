import subprocess
import tempfile
from pathlib import Path

from pdfminer.high_level import extract_text


def ocr_pdf(
    pdf_path: str | Path,
    language: str = "deu",
    dpi: int = 300,
) -> str:
    """
    Run OCR on a PDF using ocrmypdf CLI and extract text with pdfminer.

    Args:
        pdf_path: Path to the PDF file.
        language: Tesseract language code (e.g., 'deu', 'eng').
        dpi: Resolution for OCR processing.

    Returns:
        Extracted text from all pages.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / "ocr_output.pdf"
        sidecar_path = Path(tmp_dir) / "ocr_output.txt"

        cmd = [
            "ocrmypdf",
            "--language", language,
            "--force-ocr",
            "--deskew",
            "--oversample", str(dpi),
            "--image-dpi", str(dpi),
            "--sidecar", str(sidecar_path),
            str(pdf_path),
            str(output_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"ocrmypdf failed:\nstdout: {result.stdout}\nstderr: {result.stderr}")

        # Prefer sidecar text file (raw Tesseract output)
        if sidecar_path.exists():
            text = sidecar_path.read_text(encoding="utf-8")
            if text.strip():
                return text

        # Fallback: extract from the OCR'd PDF
        return extract_text(str(output_path))


if __name__ == "__main__":
    raw_text = ocr_pdf("example.pdf")
    print(raw_text)
