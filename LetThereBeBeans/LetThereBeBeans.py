# main.py
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl

from automation_clusters import HyperSpectral
from cores import XWing
from cores import Cornerstone



def main():
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    HyperSpectralBackend = HyperSpectral()
    # Make "backend" visible to QML (what we used in the .qml file)
    engine.rootContext().setContextProperty("CornerstoneBackend", HyperSpectralBackend)
    engine.rootContext().setContextProperty("XWingBackend", HyperSpectralBackend)
    engine.rootContext().setContextProperty("MasterCoreBackend", HyperSpectralBackend)

    qml_file = Path(__file__).resolve().parent / "components/main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))


    sys.exit(app.exec())


if __name__ == "__main__":
    main()
