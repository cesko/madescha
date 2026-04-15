import sys
import os
import argparse
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCommandLineParser, QCommandLineOption

from madescha.gui.mainwindow import MainWindow
from madescha.core.datatypes import DocumentInfo, Date, AutoProcessingStatus

from PySide6.QtCore import QObject, Signal

class Madescha(QObject):
    pdf_loaded = Signal(str)
    pdf_load_failed = Signal(str)
    auto_processing_status_changed = Signal(AutoProcessingStatus)

    def __init__(self):
        super().__init__()

        self._document_path = None

    def open_document(self, path:str):
        if os.path.exists(path):
            self._document_path = path
            self.pdf_loaded.emit(self._document_path)

    def close_document(self):
        self._document_path = None
        pass

        
    def run_ocr(self):
        pass

    def run_llm(self):
        pass


def main():
    parser = argparse.ArgumentParser(description="Madescha - Mach deine Scheiß Ablage!\nA little tool to help sort important documents.")
    parser.add_argument("file", nargs="?", help="PDF file to open.")
    parser.add_argument("--cli", action="store_true", help="Run in command-line mode instead of GUI mode.")
    args = parser.parse_args()

    if args.cli:
        cli(args.file)
    else:
        gui(args.file)


def cli(file=None):
    if file:
        print(f"Opening PDF: {file}")
        print(f"Not implemented")
        
    else:
        print("No file specified.")


def gui(file=None):
    app = QApplication(sys.argv)
    app.setApplicationName("Madescha")
    app.setApplicationVersion("0.0.1")

    madescha = Madescha()

    window = MainWindow()

    window.file_selected.connect(madescha.open_document)
    madescha.pdf_loaded.connect(window.open_pdf)

    window.show()

    if file:
        madescha.open_document(file)

    sys.exit(app.exec())




if __name__ == "__main__":
    main()
