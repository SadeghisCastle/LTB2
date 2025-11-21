# main.py
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl

from pretend_cores import XWing
from pretend_cores import Cornerstone



def main():
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    XWingBackend = XWing()
    CornerstoneBackend = Cornerstone()
    # Make "backend" visible to QML (what we used in the .qml file)
    engine.rootContext().setContextProperty("CornerstoneBackend", CornerstoneBackend)
    engine.rootContext().setContextProperty("backend", XWingBackend)

    qml_file = Path(__file__).resolve().parent / "components/CornerstoneController.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))


    sys.exit(app.exec())


if __name__ == "__main__":
    main()
    print("hello?")
