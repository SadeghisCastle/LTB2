from PySide6.QtCore import QObject, Signal, Property, Slot
import time

class XWing(QObject):
    
    xChanged = Signal()
    yChanged = Signal()

    def __init__(self):
        super().__init__()  # Add this
        self._x = 0.0
        self._y = 0.0
        self._home_x = 0.0
        self._home_y = 0.0
        self._step = 1.0
        self.rate = 50  # Add this
        # self.ac = ArduinoClient("COM4", 115200)  # Commented out for pretend
        self.coordinates = []
        print("XWing (pretend) initialized")

    @Property(float, notify=xChanged)
    def xPos(self):
        return self._x

    @Property(float, notify=yChanged)
    def yPos(self):
        return self._y

    @Property(str, notify=xChanged)
    def xPosString(self):
        return f"{self._x:.2f}"

    @Property(str, notify=yChanged)
    def yPosString(self):
        return f"{self._y:.2f}"

    @Slot()
    def moveUp(self):
        self._y += self._step
        # self.ac.commandSend(f"G1 Y{self._y} F{self.rate}")  # Pretend - no hardware
        print("Move Up ->", self._y)
        self.yChanged.emit()

    @Slot()
    def moveDown(self):
        self._y -= self._step
        # self.ac.commandSend(f"G1 Y{self._y} F{self.rate}")  # Pretend - no hardware
        print("Move Down ->", self._y)
        self.yChanged.emit()

    @Slot()
    def moveRight(self):
        self._x += self._step
        # self.ac.commandSend(f"G1 X{self._x} F{self.rate}")  # Pretend - no hardware
        print("Move Right ->", self._x)
        self.xChanged.emit()

    @Slot()
    def moveLeft(self):
        self._x -= self._step
        # self.ac.commandSend(f"G1 X{self._x} F{self.rate}")  # Pretend - no hardware
        print("Move Left ->", self._x)
        self.xChanged.emit()

    @Slot()
    def home(self):
        # self.ac.commandSend(f"G1 X{0} Y{0} F{self.rate}")  # Pretend - no hardware
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
        # self.ac.commandSend(f"G1 X{x_str} Y{y_str} F{self.rate}")  # Pretend - no hardware
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

    @Slot(float, float)
    def storeCoordinates(self, x, y):
        self.coordinates.append((self._x, self._y))
        print(self.coordinates)

    @Slot()
    def recall(self):
        for i in range(len(self.coordinates)):
            self._x = self.coordinates[i][0]
            self._y = self.coordinates[i][1]
            print(self._x, self._y)
            time.sleep(2)
            self.xChanged.emit()
            self.yChanged.emit()


class Cornerstone(QObject):
    waveChanged = Signal()
    shutterChanged = Signal()
    startWavelengthChanged = Signal()
    endWavelengthChanged = Signal()
    numStepsChanged = Signal()

    def __init__(self):
        super().__init__()  # Add this
        # self.mono = CornerstoneClient("helpers/cornerstone_helper.exe")  # Commented for pretend
        self.currentWavelength = 10.0  # Change to float
        self.targetWavelength = 630
        self.shutterState = "Closed"  # Match real version
        self.startWavelength = 550.0
        self.endWavelength = 1000.0
        self.numSteps = 450
        self.currentGrating = 2
        print("Cornerstone (pretend) initialized")

    @Property(str, notify=waveChanged)
    def wavePos(self):
        return f"{self.currentWavelength:.2f}"  # Fix: format as string

    @Property(str, notify=shutterChanged)
    def shutterPos(self):
        return self.shutterState

    @Property(int, notify=numStepsChanged)
    def numStepsValue(self):
        return self.numSteps
    
    @Slot(str)
    def setNumSteps(self, value_str):
        self.numSteps = int(value_str)
        self.numStepsChanged.emit()
        print(self.numSteps)

    @Property(float, notify=startWavelengthChanged)
    def startWavelengthValue(self):
        return self.startWavelength
    
    @Property(float, notify=endWavelengthChanged)
    def endWavelengthValue(self):
        return self.endWavelength
    
    @Slot(str)
    def setStartWavelength(self, value_str):
        self.startWavelength = float(value_str)
        self.startWavelengthChanged.emit()
        print(self.startWavelength)
    
    @Slot(str)
    def setEndWavelength(self, value_str):
        self.endWavelength = float(value_str)
        self.endWavelengthChanged.emit()
        print(self.endWavelength)
    
    @Slot(str)
    def setWavelength(self, target_str):
        self.targetWavelength = float(target_str)
        self.currentWavelength = float(target_str)  # Fix: convert to float
        # self.mono.goto(self.targetWavelength)  # Pretend - no hardware
        self.waveChanged.emit()
        print('Wavelength set to', self.currentWavelength)

    @Slot()
    def openShutter(self):
        # self.mono.open_shutter()  # Pretend - no hardware
        print("Shutter opened")
        self.shutterState = "Open"
        self.shutterChanged.emit()

    @Slot()
    def closeShutter(self):
        # self.mono.close_shutter()  # Pretend - no hardware
        print("Shutter closed")
        self.shutterState = "Closed"
        self.shutterChanged.emit()