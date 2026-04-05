import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCommandLineParser, QCommandLineOption

from mainwindow import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("PDF Viewer")
    app.setApplicationVersion("1.0")

    parser = QCommandLineParser()
    parser.setApplicationDescription("A simple PDF viewer.")
    parser.addHelpOption()
    parser.addVersionOption()
    parser.addPositionalArgument("file", "PDF file to open.", "[file]")
    parser.process(app)

    positional = parser.positionalArguments()

    window = MainWindow()
    window.show()

    if positional:
        window.open_pdf(positional[0])

    sys.exit(app.exec())
