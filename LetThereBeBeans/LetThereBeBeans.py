# main.py
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl
from PySide6 import QtGui
from automation_clusters import HyperSpectral, QuickScanAutomation
from pretend_cores import XWing, Cornerstone



def main():
    # importing fonts



    # Creating app
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Importing cores
    xwing = XWing()
    cornerstone = Cornerstone()
    quick_scan = QuickScanAutomation(xwing, cornerstone)

    # Make "backend" visible to QML (what we used in the .qml file)
    engine.rootContext().setContextProperty("CornerstoneBackend", cornerstone)
    engine.rootContext().setContextProperty("XWingBackend", xwing)
    engine.rootContext().setContextProperty("QuickScanBackend", quick_scan)

    qml_file = Path(__file__).resolve().parent / "components/main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))


    sys.exit(app.exec())


if __name__ == "__main__":
    main()
