from PySide6.QtCore import QObject, Signal, Property, Slot, QThread
from hardware_controllers import *
from cores import XWing, Cornerstone

class Spectrum(QObject):
    finished = Signal()
    progress = Signal(float, float, float, float)
    
    def __init__(self, coordinates, start_wl, end_wl, num_steps, ac, mono, digi, rate):
        super().__init__()
        self.coordinates = coordinates
        self.start_wl = start_wl
        self.end_wl = end_wl
        self.num_steps = num_steps
        self.ac = ac
        self.mono = mono
        self.digi = digi
        self.rate = rate
        self._is_running = True
    
    def run(self):
        step_size = (self.end_wl - self.start_wl) / (self.num_steps - 1)
        self.mono.open_shutter()
        for i in range(len(self.coordinates)):
            if not self._is_running:
                break
                
            x, y = self.coordinates[i]
            self.ac.commandSend(f"G1 X{x} Y{y} F{self.rate}")
            
            for j in range(self.num_steps):
                if not self._is_running:
                    break
                    
                wavelength = self.start_wl + j * step_size
                self.mono.goto(wavelength)
                time.sleep(0.5)
                data = 1 # placeholder
                self.progress.emit(x, y, wavelength, data)
                time.sleep(2)
        
        self.finished.emit()
        print("Dunzo bununzo!")
    
    def stop(self):
        self._is_running = False

class HyperSpectral(QObject):
    xChanged = Signal()
    yChanged = Signal()
    waveChanged = Signal()
    shutterChanged = Signal()
    startWavelengthChanged = Signal()
    endWavelengthChanged = Signal()
    numStepsChanged = Signal()

    def __init__(self):
        super().__init__()
        self._x = 0.0
        self._y = 0.0
        self._home_x = 0.0
        self._home_y = 0.0
        self._step = 1.0 
        self.rate = 50
        self.ac = ArduinoClient("COM4", 115200)
        print('X-Wing Online')
        self.coordinates = []
        self.mono = CornerstoneClient("LetThereBeBeans/helpers/cornerstone_helper.exe")
        self.mono.open()
        self.currentWavelength = 10.0
        self.targetWavelength = 630
        self.shutterState = "Open"
        self.startWavelength = 550
        self.endWavelength = 1000
        self.numSteps = 450
        self.currentGrating = 2
        self.scan_thread = None
        self.scan = None
        
        print("Cornerstone Online")

        self.digi = NIScopeClient()
        print("Digitizer online")
    
    # X-Wing Properties
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

    # Cornerstone Properties
    @Property(str, notify= waveChanged)
    def wavePos(self):
        return str(self.currentWavelength)

    @Property(str, notify = shutterChanged)
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

    # X-Wing Slots
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
        # Make sure we can't run a scan if one is already going
        if self.scan_thread is not None and self.scan_thread.isRunning():
            print("Hold ur horses...")
            return
        
        # Create the object that will scan on a different thread
        self.scan = Spectrum(
            self.coordinates,
            self.startWavelength,
            self.endWavelength,
            self.numSteps,
            self.ac,
            self.mono,
            self.digi,
            self.rate
        )

        # Create the thread
        self.scan_thread = QThread()
        
        # Tell the object what thread it will run on
        self.scan.moveToThread(self.scan_thread)
        
        # Connect the signals from the object running on the thread to the main thread like we saw in the tutorial
        self.scan_thread.started.connect(self.scan.run)
        self.scan.finished.connect(self.scan_thread.quit)
        self.scan.finished.connect(self.scan.deleteLater)
        self.scan_thread.finished.connect(self.scan_thread.deleteLater)
        # As an example, here progress is connected to updateScanProgress so whenever progress is 
        # emitted, it calls updateScanProgress which then emits all the individual signals
        self.scan.progress.connect(self._updateScanProgress)
        
        # Run the automation
        self.scan_thread.start()
        print("Scan started")
    
    def _updateScanProgress(self, x, y, wavelength, data):
        """Updates Properties from within the threaded process because the thread will 
           only return once at the end if this isn't called from within the thread"""
        self._x = x
        self._y = y
        self.currentWavelength = wavelength
        self.xChanged.emit()
        self.yChanged.emit()
        self.waveChanged.emit()
        print(f"Position: ({x}, {y}), Wavelength: {wavelength:.2f}")
    
    @Slot()
    def stopScan(self):
        """Stop the scan"""
        if self.scan:
            self.scan.stop()
            print("Stopping scan...")
    
    # Cornerstone Properties
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
    def setWavelength(self, target_Str):
        self.targetWavelength = float(target_Str)
        self.currentWavelength = target_Str
        self.mono.goto(self.targetWavelength)
        self.waveChanged.emit()
        print('all good')

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



    
