from PySide6.QtCore import QObject, Signal, Property, Slot
from hardware_controllers import *

class XWing(QObject):

    xChanged = Signal()
    yChanged = Signal()

    def __init__(self):
        super().__init__()
        self._x = 0.0
        self._y = 0.0
        self._home_x = 0.0
        self._home_y = 0.0
        self._step = 1.0  # mm per button press (change as needed)

    # --- X position as a float (if you ever want numeric binding) ---
    @Property(float, notify=xChanged)
    def xPos(self):
        return self._x

    # --- Y position ---
    @Property(float, notify=yChanged)
    def yPos(self):
        return self._y

    # --- String versions for your labels ---
    @Property(str, notify=xChanged)
    def xPosString(self):
        return f"{self._x:.2f}"

    @Property(str, notify=yChanged)
    def yPosString(self):
        return f"{self._y:.2f}"

    # --- Movement slots (called from QML) ---
    @Slot()
    def moveUp(self):
        self._y += self._step
        print("Move Up ->", self._y)
        self.yChanged.emit()

    @Slot()
    def moveDown(self):
        self._y -= self._step
        print("Move Down ->", self._y)
        self.yChanged.emit()

    @Slot()
    def moveRight(self):
        self._x += self._step
        print("Move Right ->", self._x)
        self.xChanged.emit()

    @Slot()
    def moveLeft(self):
        self._x -= self._step
        print("Move Left ->", self._x)
        self.xChanged.emit()

    @Slot()
    def home(self):
        self._x = self._home_x
        self._y = self._home_y
        print("Go Home ->", self._x, self._y)
        self.xChanged.emit()
        self.yChanged.emit()

    @Slot()
    def setHome(self):
        self._home_x = self._x
        self._home_y = self._y
        print("Set Home ->", self._home_x, self._home_y)

    @Slot(str, str)
    def setPosition(self, x_str, y_str):
        try:
            if x_str.strip():
                self._x = float(x_str)
            if y_str.strip():
                self._y = float(y_str)
            print("Set Position ->", self._x, self._y)
            self.xChanged.emit()
            self.yChanged.emit()
        except ValueError:
            print("Invalid position input:", x_str, y_str)

class Cornerstone(QObject):
    waveChanged =  Signal()
    shutterChanged = Signal()

    def __init__(self):
        super().__init__()
        #self.mono = CornerstoneClient("helpers/cornerstone_helper.exe")
        self.currentWavelength = 10
        self.targetWavelength = 630
        self.shutterState = "Open"
        self.startWavelength = 550
        self.endWavelength = 1000
        self.numSteps = 450
        self.currentGrating = 2
        print("all good")


    @Property(str, notify= waveChanged)
    def wavePos(self):
        return self.currentWavelength

    @Property(str, notify = shutterChanged)
    def shutterPos(self):
        return self.shutterState
    
    @Slot(str)
    def setWavelength(self, target_Str):
        self.targetWavelength = float(target_Str)
        self.currentWavelength = target_Str
        #self.mono.goto(targetWavelength)
        self.waveChanged.emit()
        print('all good')

    @Slot()
    def openShutter(self):
        #self.mono.open_shutter()
        print("Shutter opened")
        self.shutterState = "Open"
        self.shutterChanged.emit()

    @Slot()
    def closeShutter(self):
        #self.mono.close_shutter()
        print("Shutter closed")
        self.shutterState = "Closed"
        self.shutterChanged.emit()