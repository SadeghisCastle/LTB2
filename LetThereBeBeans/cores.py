from PySide6.QtCore import QObject, Signal, Property, Slot
from hardware_controllers import *

""" Create QObject classes for each hardware controller then 
just copy and paste the slots, signals, and properties to
MasterCore so it can be simply used in automations """
class XWing(QObject):
    
    
    xChanged = Signal()
    yChanged = Signal()

    def __init__(self):
        self._x = 0.0
        self._y = 0.0
        self._home_x = 0.0
        self._home_y = 0.0
        self._step = 1.0  # mm per button press (change as needed)
        self.rate = 50
        self.ac = ArduinoClient("COM4", 115200)
        print('all good')
        self.coordinates = []
        

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
        self.ac.commandSend(f"G1 Y{self._y} F{self.rate}")
        print("Move Up ->", self._y)
        self.yChanged.emit()

    @Slot()
    def moveDown(self):
        
        self._y -= self._step
        self.ac.commandSend(f"G1 Y{self._y} F{self.rate}")
        print("Move Down ->", self._y)
        self.yChanged.emit()

    @Slot()
    def moveRight(self):
        
        self._x += self._step
        self.ac.commandSend(f"G1 X{self._x} F{self.rate}")
        print("Move Right ->", self._x)
        self.xChanged.emit()

    @Slot()
    def moveLeft(self):
        
        self._x -= self._step
        self.ac.commandSend(f"G1 X{self._x} F{self.rate}")
        print("Move Left ->", self._x)
        self.xChanged.emit()

    @Slot()
    def home(self):
        self.ac.commandSend(f"G1 X{0} Y{0} F{self.rate}")
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
        self.ac.commandSend(f"G1 X{x_str} Y{y_str} F{self.rate}")
        if x_str.strip():
            self._x = float(x_str)
        if y_str.strip():
            self._y = float(y_str)
        print("Set Position ->", self._x, self._y)
        self.xChanged.emit()
        self.yChanged.emit()

    @Slot(float, float)
    def storeCoordinates(self, x, y):
        self.coordinates.append((self._x,self._y))
        print(self.coordinates)

    @Slot()
    def recall(self):
        print("Meow")


class Cornerstone(QObject):
    waveChanged = Signal()
    shutterChanged = Signal()
    startWavelengthChanged = Signal()
    endWavelengthChanged = Signal()
    numStepsChanged = Signal()
    
    def __init__(self):
        self.mono = CornerstoneClient("LetThereBeBeans/helpers/cornerstone_helper.exe")
        self.mono.open()
        self.targetWavelength = 630
        self.shutterState = "Closed"
        self.startWavelength = 550
        self.endWavelength = 1000
        self.numSteps = 450
        self.currentGrating = 3
        self.currentWavelength = 0.0
        print("Cornerstone online")
    
    @Property(str, notify=waveChanged)
    def wavePos(self):
        return str(self.currentWavelength)
    
    @Property(str, notify=shutterChanged)
    def shutterPos(self):
        return self.shutterState
    
    @Property(float, notify=startWavelengthChanged)
    def startWavelengthValue(self):
        return self.startWavelength
    
    @Property(float, notify=endWavelengthChanged)
    def endWavelengthValue(self):
        return self.endWavelength
    
    @Property(int, notify=numStepsChanged)
    def numStepsValue(self):
        return self.numSteps
    
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
    def setNumSteps(self, value_str):
        self.numSteps = int(value_str)
        self.numStepsChanged.emit()
        print(self.numSteps)
    
    @Slot(str)
    def setWavelength(self, target_str):
        self.targetWavelength = float(target_str)
        self.mono.goto(self.targetWavelength)
        
        while self.mono.position() == -1:
            time.sleep(0.1)
        
        self.currentWavelength = self.mono.position()
        self.waveChanged.emit()
        print('Wavelength set')
    
    @Slot()
    def openShutter(self):
        self.mono.open_shutter()
        print("Shutter opened")
        self.shutterState = "Open"
        self.shutterChanged.emit()
    
    @Slot()
    def closeShutter(self):
        self.mono.close_shutter()
        print("Shutter closed")
        self.shutterState = "Closed"
        self.shutterChanged.emit()


class MasterCore(XWing, Cornerstone): # Add new cores here
    """ Combined class with all cores. """
    # Re-declare all signals 
    xChanged = Signal()
    yChanged = Signal()
    waveChanged = Signal()
    shutterChanged = Signal()
    startWavelengthChanged = Signal()
    endWavelengthChanged = Signal()
    numStepsChanged = Signal()
    
    def __init__(self): # Initialize new cores here
        QObject.__init__(self)
        XWing.__init__(self)
        Cornerstone.__init__(self)
        print("MasterCore initialized")
    
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
    
    # Cornerstone properties
    @Property(str, notify=waveChanged)
    def wavePos(self):
        return str(self.currentWavelength)
    
    @Property(str, notify=shutterChanged)
    def shutterPos(self):
        return self.shutterState
    
    @Property(float, notify=startWavelengthChanged)
    def startWavelengthValue(self):
        return self.startWavelength
    
    @Property(float, notify=endWavelengthChanged)
    def endWavelengthValue(self):
        return self.endWavelength
    
    @Property(int, notify=numStepsChanged)
    def numStepsValue(self):
        return self.numSteps
    
    # --- Movement slots (called from QML) ---
    @Slot()
    def moveUp(self):
        XWing.moveUp(self)

    @Slot()
    def moveDown(self):
        XWing.moveDown(self)

    @Slot()
    def moveRight(self):
        XWing.moveRight(self)

    @Slot()
    def moveLeft(self):
        XWing.moveLeft(self)

    @Slot()
    def home(self):
        XWing.home(self)

    @Slot()
    def setHome(self):
        XWing.setHome(self)

    @Slot(str, str)
    def setPosition(self, x_str, y_str):
        XWing.setPosition(self, x_str, y_str)

    @Slot(float, float)
    def storeCoordinates(self, x, y):
        XWing.storeCoordinates(self, x, y)

    @Slot()
    def recall(self):
        XWing.recall(self)
    
    # Cornerstone slots
    @Slot(str)
    def setStartWavelength(self, value_str):
        Cornerstone.setStartWavelength(self, value_str)
    
    @Slot(str)
    def setEndWavelength(self, value_str):
        Cornerstone.setEndWavelength(self, value_str)
    
    @Slot(str)
    def setNumSteps(self, value_str):
        Cornerstone.setNumSteps(self, value_str)
    
    @Slot(str)
    def setWavelength(self, target_str):
        Cornerstone.setWavelength(self, target_str)
    
    @Slot()
    def openShutter(self):
        Cornerstone.openShutter(self)
    
    @Slot()
    def closeShutter(self):
        Cornerstone.closeShutter(self)