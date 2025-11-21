# backend.py
from PySide6.QtCore import QObject, Signal, Property, Slot
import arduino_client as ac


class Backend(QObject):

    xChanged = Signal()
    yChanged = Signal()

    def __init__(self):
        super().__init__()
        self._x = 0.0
        self._y = 0.0
        self._home_x = 0.0
        self._home_y = 0.0
        self._step = 1.0  # mm per button press (change as needed)
        self.rate = 300
        self.baudRate = 115200
        self.devPort = ac.serialInit("COM4", self.baudRate)
        print('all good')
        

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
        
        print('all good')
        self._y += self._step
        ac.commandSend(self.devPort, f"G1 Y{self._y} F{self.rate}", self.baudRate)
        print("Move Up ->", self._y)
        self.yChanged.emit()

    @Slot()
    def moveDown(self):
        
        self._y -= self._step
        ac.commandSend(self.devPort, f"G1 Y{self._y} F{self.rate}", self.baudRate)
        print("Move Down ->", self._y)
        self.yChanged.emit()

    @Slot()
    def moveRight(self):
        
        self._x += self._step
        ac.commandSend(self.devPort, f"G1 X{self._x} F{self.rate}", self.baudRate)
        print("Move Right ->", self._x)
        self.xChanged.emit()

    @Slot()
    def moveLeft(self):
        
        self._x -= self._step
        ac.commandSend(self.devPort, f"G1 X{self._x} F{self.rate}", self.baudRate)
        print("Move Left ->", self._x)
        self.xChanged.emit()

    @Slot()
    def home(self):
        ac.commandSend(self.devPort, f"G1 X{0} Y{0} F{self.rate}", self.baudRate)
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
        ac.commandSend(self.devPort, f"G1 X{x_str} Y{y_str} F{self.rate}", self.baudRate)
        if x_str.strip():
            self._x = float(x_str)
        if y_str.strip():
            self._y = float(y_str)
        print("Set Position ->", self._x, self._y)
        self.xChanged.emit()
        self.yChanged.emit()

