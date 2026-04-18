import sys
import os
import argparse
import threading
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCommandLineParser, QCommandLineOption, QThread

from madescha.gui.mainwindow import MainWindow
from madescha.core.datatypes import DocumentInfo, Date, AutoProcessingStatus, OcrResult, LlmResult, Document
from madescha.core.ocr_processor import OcrProcessor
from madescha.core.ollama_doc_parser import OllamaDocumentParser

from PySide6.QtCore import QObject, Signal

class MadeschaConfig():
    automatically_parse_opened_documents = True

class Madescha(QObject):
    """
    The Madescha Logic and Processing Pipeline.
    Independent of GUI but uses Qt Signals and Slots as API
    """
    pdf_loaded = Signal(str)
    pdf_load_failed = Signal(str)
    auto_processing_status_changed = Signal(AutoProcessingStatus)

    def __init__(self):
        super().__init__()
        self._config = MadeschaConfig()

        self._document_path = None

        self._ocr_processor = OcrProcessor()
        self._llm_parsier = OllamaDocumentParser()


    def open_document(self, path:str):
        if os.path.exists(path):
            self._document_path = path
            self.pdf_loaded.emit(self._document_path)

        if self._config.automatically_parse_opened_documents:
            self._auto_processing()

    def close_document(self):
        self._document_path = None
        pass
        
    def run_ocr(self) -> OcrResult:
        result = OcrResult()
        
        self._ocr_processor.open_document(self._document_path)
        try:
            self._ocr_processor.run()
        except Exception as e:
            result.success = False
            result.message = str(e)
            return result
        
        result.success = True
        result.message = "OCR done"
        result.text = self._ocr_processor.get_text()
        return result
    

    def run_llm(self, content:str|None = None) -> LlmResult:
        if content is None:
            content = self._ocr_processor.get_text()
        if content == "":
            return LlmResult(DocumentInfo(), False, "Empty string provided! Maybe OCR did not produce anything?")
        
        try:
            doc_info = self._llm_parsier.get_document_info(content)
            return LlmResult(doc_info, True, "LLM parsing done")

        except Exception as e:
            return LlmResult(Document(), False, str(e))
            
    
    def _auto_processing(self):
        status = AutoProcessingStatus(True, False, "Running OCR...")
        self.auto_processing_status_changed.emit(status)
        print(status.status_message)

        ocr_result = self.run_ocr()

        if ocr_result.success:
            status.status_message = "OCR done. Running LLM..."
            status.ocr_text = ocr_result.text
            self.auto_processing_status_changed.emit(status)
            print(status.status_message)
        else:
            status.running = False
            status.success = False
            status.status_message = ocr_result.message
            self.auto_processing_status_changed.emit(status)
            print(status.status_message)
            return
        
        llm_result = self.run_llm()

        print(llm_result.document_info)
        
        status.running = False
        status.success = llm_result.success
        status.status_message = llm_result.message
        status.fields = llm_result.document_info
        self.auto_processing_status_changed.emit(status)
        print(status.status_message)

    
    def start_auto_prosessing(self):
        return self._auto_processing()

    def stop_auto_prosessing(self):
        return self._auto_processing()




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
    worker_thread = QThread()
    madescha.moveToThread(worker_thread)

    window = MainWindow()

    window.file_selected.connect(madescha.open_document)
    madescha.pdf_loaded.connect(window.open_pdf)
    madescha.auto_processing_status_changed.connect(window.set_auto_processing)   


    # Ensure the worker thread stops cleanly when the app exits
    app.aboutToQuit.connect(worker_thread.quit)
    app.aboutToQuit.connect(worker_thread.wait)

    worker_thread.start()
    window.show()

    if file:
        # Emit through the signal to ensure it runs on the worker thread
        window.file_selected.emit(file)

    sys.exit(app.exec())




if __name__ == "__main__":
    main()
