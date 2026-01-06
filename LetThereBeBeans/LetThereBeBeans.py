# main.py
import sys
from pathlib import Path
import os

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Fusion"
from PySide6.QtWidgets import QApplication, QMenuBar
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl, QObject, Slot
from PySide6.QtGui import QActionGroup
from automation_clusters import HyperSpectralExtinction, HyperSpectralSingleFluor
from cores import XWing, Cornerstone, Oscilloscope, PMTGainShield


class AutomationManager(QObject):
    """Manages switching between automation clusters"""
    def __init__(self, xwing, cornerstone, pmt_shield, engine):
        super().__init__()
        self.xwing = xwing
        self.cornerstone = cornerstone
        self.pmt_shield = pmt_shield
        self.engine = engine
        self.current_automation = None
        self.current_type = None

        # Don't initialize any automation at startup to avoid hardware conflicts
        # User must select an automation mode from the sidebar
        print("AutomationManager ready - no automation loaded. Please select a mode from the sidebar.")

    def _cleanup_current_automation(self):
        """Clean up the current automation before switching"""
        if self.current_automation is None:
            return

        # Stop any running scans
        if hasattr(self.current_automation, 'stopScan'):
            self.current_automation.stopScan()

        # Reset PMT gain to 0 (but don't close the connection - GUI needs it)
        if hasattr(self.current_automation, 'pmt'):
            try:
                self.current_automation.pmt.commandSend("0")
                print("  Reset PMT gain to 0")
            except Exception as e:
                print(f"Warning: Could not reset PMT: {e}")

        # Clear references but don't close hardware
        self.current_automation = None

        print(f"Cleaned up {self.current_type} automation")

    def _initialize_automation(self, automation_type):
        """Initialize a specific automation cluster"""
        # Clean up current automation first
        self._cleanup_current_automation()

        # Create new automation instance with shared hardware
        if automation_type == 'extinction':
            self.current_automation = HyperSpectralExtinction(self.xwing, self.cornerstone, self.pmt_shield)
            self.current_type = 'HyperSpectralExtinction'
        elif automation_type == 'single_fluor':
            self.current_automation = HyperSpectralSingleFluor(self.xwing, self.cornerstone, self.pmt_shield)
            self.current_type = 'HyperSpectralSingleFluor'

        # Update QML context
        self.engine.rootContext().setContextProperty("AutomationBackend", self.current_automation)
        print(f"Initialized automation: {self.current_type}")

    @Slot()
    def switchToExtinction(self):
        """Switch to HyperSpectralExtinction automation (callable from QML)"""
        if self.current_type != 'HyperSpectralExtinction':
            self._initialize_automation('extinction')

    @Slot()
    def switchToSingleFluor(self):
        """Switch to HyperSpectralSingleFluor automation (callable from QML)"""
        if self.current_type != 'HyperSpectralSingleFluor':
            self._initialize_automation('single_fluor')


def main():
    # Creating app
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Importing cores
    xwing = XWing()
    cornerstone = Cornerstone()
    pmt = PMTGainShield()

    # Create automation manager with shared hardware
    automation_manager = AutomationManager(xwing, cornerstone, pmt, engine)

    # Make "backend" visible to QML (what we used in the .qml file)
    engine.rootContext().setContextProperty("CornerstoneBackend", cornerstone)
    engine.rootContext().setContextProperty("XWingBackend", xwing)
    engine.rootContext().setContextProperty("AutomationManager", automation_manager)
    engine.rootContext().setContextProperty("PMTGainShieldBackend", pmt)

    qml_file = Path(__file__).resolve().parent / "components/main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))

    # Get the root QML window to add menu bar
    if not engine.rootObjects():
        sys.exit(-1)

    root = engine.rootObjects()[0]

    # Create menu bar
    menu_bar = QMenuBar()
    automation_menu = menu_bar.addMenu("&Automation")

    # Add menu items for each automation cluster
    extinction_action = automation_menu.addAction("HyperSpectral Extinction")
    extinction_action.triggered.connect(automation_manager.switchToExtinction)
    extinction_action.setCheckable(True)

    single_fluor_action = automation_menu.addAction("HyperSpectral SingleFluor")
    single_fluor_action.triggered.connect(automation_manager.switchToSingleFluor)
    single_fluor_action.setCheckable(True)

    # Create action group for mutual exclusivity
    action_group = QActionGroup(menu_bar)
    action_group.addAction(extinction_action)
    action_group.addAction(single_fluor_action)

    # Attach menu bar to the window
    if hasattr(root, 'setMenuBar'):
        root.setMenuBar(menu_bar)
    else:
        # For QML windows, we need to show the menu bar separately
        menu_bar.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
