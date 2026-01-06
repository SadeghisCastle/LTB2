# main.py
import sys
from pathlib import Path
import os
import time

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Fusion"
from PySide6.QtWidgets import QApplication, QMenuBar
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl, QObject, Slot
from PySide6.QtGui import QActionGroup
from automation_clusters import HyperSpectralExtinction, HyperSpectralSingleFluor
from cores import XWing, Cornerstone, Oscilloscope, PMTGainShield


class AutomationManager(QObject):
    """Manages switching between automation clusters"""
    def __init__(self, xwing, cornerstone, engine):
        super().__init__()
        self.xwing = xwing
        self.cornerstone = cornerstone
        self.engine = engine
        self.current_automation = None
        self.current_type = None

        # Initialize with default automation
        self._initialize_automation('single_fluor')

    def _cleanup_current_automation(self):
        """Clean up the current automation before switching"""
        if self.current_automation is None:
            return

        # Stop any running scans
        if hasattr(self.current_automation, 'stopScan'):
            self.current_automation.stopScan()

        # Close hardware connections that need cleanup
        if hasattr(self.current_automation, 'pmt'):
            try:
                self.current_automation.pmt.commandSend("0")  # Turn off PMT
                time.sleep(0.5)  # Give it time to process
                if hasattr(self.current_automation.pmt, 'serialClose'):
                    self.current_automation.pmt.serialClose()
                    print("  Closed PMT serial connection")
            except Exception as e:
                print(f"Warning: Could not clean up PMT: {e}")

        # NIScopeClient doesn't need explicit cleanup (uses context manager)
        # but we can clear the reference
        if hasattr(self.current_automation, 'digi'):
            self.current_automation.digi = None

        print(f"Cleaned up {self.current_type} automation")

    def _initialize_automation(self, automation_type):
        """Initialize a specific automation cluster"""
        # Clean up current automation first
        self._cleanup_current_automation()

        # Create new automation instance
        if automation_type == 'hyperspectral':
            self.current_automation = HyperSpectral(self.xwing, self.cornerstone)
            self.current_type = 'HyperSpectral'
        elif automation_type == 'extinction':
            self.current_automation = HyperSpectralExtinction(self.xwing, self.cornerstone)
            self.current_type = 'HyperSpectralExtinction'
        elif automation_type == 'single_fluor':
            self.current_automation = HyperSpectralSingleFluor(self.xwing, self.cornerstone)
            self.current_type = 'HyperSpectralSingleFluor'

        # Update QML context
        self.engine.rootContext().setContextProperty("AutomationBackend", self.current_automation)
        print(f"Initialized automation: {self.current_type}")

    @Slot()
    def switchToHyperspectral(self):
        """Switch to HyperSpectral automation (callable from QML)"""
        if self.current_type != 'HyperSpectral':
            self._initialize_automation('hyperspectral')

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

    # Create automation manager
    automation_manager = AutomationManager(xwing, cornerstone, engine)

    # Make "backend" visible to QML (what we used in the .qml file)
    engine.rootContext().setContextProperty("CornerstoneBackend", cornerstone)
    engine.rootContext().setContextProperty("XWingBackend", xwing)
    engine.rootContext().setContextProperty("AutomationManager", automation_manager)
    engine.rootContext().setContextProperties("PMTGainShieldBackend", pmt)

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

    single_fluor_action = automation_menu.addAction("HyperSpectral SingleFluor")
    single_fluor_action.triggered.connect(automation_manager.switchToSingleFluor)
    single_fluor_action.setCheckable(True)
    single_fluor_action.setChecked(True)  # Default selection

    # Make actions checkable and mutually exclusive
    extinction_action.setCheckable(True)

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
