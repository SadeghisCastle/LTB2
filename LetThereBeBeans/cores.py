from PySide6.QtCore import QObject, Signal, Property, Slot, QThread
from PySide6.QtWidgets import QFileDialog
from hardware_controllers import *
import pyqtgraph as pg


""" Create QObject classes for each hardware controller then 
just copy and paste the slots, signals, and properties to
MasterCore so it can be simply used in automations """
class Worker(QObject):
    """ Object that creates a thread for automation logic then moves logic
    to that thread. All you have to do is create the object with the function 
    that you want to run on a separate thread. """
    finished = Signal()
    error = Signal(str)
    
    def __init__(self, func):
        """ Passes the function, sets _is_running to true to denote
        that a proccess is running. """
        super().__init__()
        self.func = func
        self._is_running = True
        self.thread = None
    
    def start(self):
        """Automatically create thread and start it"""
        self.thread = QThread()
        
        # Move object (i.e. anything that uses self) to the thread
        self.moveToThread(self.thread)
        
        # Connect QThread signals. Have to use this if using the QThread object.
        self.thread.started.connect(self.run)
        self.finished.connect(self.thread.quit)
        self.finished.connect(self.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # Start the thread
        self.thread.start()
    
    def run(self):
        """ Execute the function that was passed """
        self.func()
        self.finished.emit()
    
    def stop(self):
        """ Stop button for later use """
        self._is_running = False
    
    def is_running(self):
        """ Checks if thread is still running """
        return self.thread is not None and self.thread.isRunning()

class XWing(QObject):
    
    
    xChanged = Signal()
    yChanged = Signal()

    def __init__(self):
        super().__init__()
        self._x = 0.0
        self._y = 0.0
        self._home_x = 0.0
        self._home_y = 0.0
        self._step = 0.1  # mm per button press (change as needed)
        self.rate = 50
        self.ac = ArduinoClient("COM7", 115200)
        self.coordinates = []
        print("XWing online")
        

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

class Cornerstone(QObject):
    waveChanged = Signal()
    shutterChanged = Signal()
    startWavelengthChanged = Signal()
    endWavelengthChanged = Signal()
    numStepsChanged = Signal()
    
    def __init__(self):
        super().__init__()
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

class LivePlot(QObject):
    """ Creates a window with live plot """
    
    def __init__(self):
        
        # Create plot window
        self.plot_window = pg.plot(title=" Live Plot ")
        self.plot_window.setLabel('left', 'Counts')
        self.plot_window.setLabel('bottom', 'Wavelength', units='nm')
        self.plot_window.showGrid(x=True, y=True)
        self.plot_curve = self.plot_window.plot(pen='y')
        
        # Current position data
        self.wavelengths = []
        self.measurements = []
    
    def resetPlot(self):
        """Reset plot"""
        self.wavelengths = []
        self.measurements = []
        self.plot_curve.setData([], [])
    
    def updatePlot(self, wavelength, measurement):
        """Add a data point and update plot"""
        self.wavelengths.append(wavelength)
        self.measurements.append(measurement)
        self.plot_curve.setData(self.wavelengths, self.measurements)
        pg.QtWidgets.QApplication.processEvents()  # Force GUI update
    
    def closeClose(self):
        """Close the plot window"""
        if self.plot_window:
            self.plot_window.close()

class Oscilloscope(QObject):
    """Live oscilloscope waveform viewer"""
    
    def __init__(self):
        super().__init__()
        
        self.digi = NIScopeClient()
        
        # Create plot window
        self.plot_window = pg.plot(title="Oscilloscope")
        self.plot_window.setLabel('left', 'Voltage', units='V')
        self.plot_window.setLabel('bottom', 'Sample')
        self.plot_window.showGrid(x=True, y=True)
        self.plot_curve = self.plot_window.plot(pen='y')
        
        self.is_viewing = False
        self.viewer_worker = None
        
        print("Oscilloscope initialized")
    
    @Slot()
    def startLiveView(self):
        """Start continuous live viewing"""
        if self.is_viewing:
            print("Already viewing")
            return
        
        self.is_viewing = True
        self.viewer_worker = Worker(self._liveViewLoop)
        self.viewer_worker.start()
        print("Live view started")
    
    def _liveViewLoop(self):
        """Continuously capture and display waveforms"""
        while self.viewer_worker._is_running and self.is_viewing:
            try:
                # Capture waveform
                with niscope.Session("Dev1") as session:
                    session.channels[1].configure_vertical(range=40.0, coupling=niscope.VerticalCoupling.DC)
                    session.configure_horizontal_timing(
                        min_sample_rate=5000000,
                        min_num_pts=500,
                        ref_position=50.0,
                        num_records=1,
                        enforce_realtime=True
                    )
                
                    with session.initiate():
                        waveforms = session.channels[1].fetch()
                
                wfm = waveforms[0]
                samples = np.array(wfm.samples)
                
                # Update plot (PyQtGraph is thread-safe for this)
                self.plot_curve.setData(samples)
                
            except Exception as e:
                print(f"Error in live view: {e}")
                break
        
        print("Live view stopped")
    
    @Slot()
    def stopLiveView(self):
        """Stop live viewing"""
        self.is_viewing = False
        if self.viewer_worker:
            self.viewer_worker.stop()
        print("Stopping live view...")
    
    @Slot()
    def captureSingle(self):
        """Capture and display a single waveform"""
        try:
            with niscope.Session("Dev1") as session:
                session.channels[1].configure_vertical(range=40.0, coupling=niscope.VerticalCoupling.DC)
                session.configure_horizontal_timing(
                    min_sample_rate=5000000,
                    min_num_pts=5000000,
                    ref_position=50.0,
                    num_records=1,
                    enforce_realtime=True
                )
            
                with session.initiate():
                    waveforms = session.channels[1].fetch()
            
            wfm = waveforms[0]
            samples = np.array(wfm.samples)
            
            # Update plot
            self.plot_curve.setData(samples)
            print(f"Captured {len(samples)} samples")
            
        except Exception as e:
            print(f"Error capturing: {e}")
    
    def closePlot(self):
        """Close the plot window"""
        self.stopLiveView()
        if self.plot_window:
            self.plot_window.close()

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
        print("MasterCore online")

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

    @Slot(str)
    def setSaveLocation(self, path):
        """Receive the selected path from QML"""
        self.save_directory = path
        print(f"Save location set to: {path}")