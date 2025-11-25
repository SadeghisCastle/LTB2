from PySide6.QtCore import QObject, Signal, Property, Slot, QThread
from hardware_controllers import *
from cores import XWing, Cornerstone

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

class HyperSpectral(XWing, Cornerstone):
    """ First automation. We can create the required objects from cores.py and 
    use them in this new object. We aren't using functions from them, but when the code executes a command, 
    it will search through the objects that we initialize until it finds one that fits. """

    def __init__(self):
        # We aren't initializing these objects in a traditional way since we aren't using function calls from them. 
        XWing.__init__(self)
        Cornerstone.__init__(self)

    @Slot()
    def recall(self):
        """ Function that ties the button to the automation logic. Using the recall button
        as a stand in until we make a gui for starting the automation """

        # Make sure we can't run a scan if one is already going
        if self.scan_thread is not None and self.scan_thread.isRunning():
            print("Hold ur horses...")
            return
        
        # Create the object that will run the automation on a different thread
        self.worker = Worker(self._runScan)
        self.worker.start()
        print("Scan started")
    
    def _runScan(self):
        """ Automation logic. The underscore is to denote that it doesn't 
        interact with the GUI and is stricly backend. """
        step_size = (self.endWavelength - self.startWavelength) / (self.numSteps - 1)
        self.mono.open_shutter()
        
        for i in range(len(self.coordinates)): # How the stop button actually stops the automation
            if not self.worker._is_running:
                break
                
            x, y = self.coordinates[i] # Gets coordinates that are stored from X-Wing
            self.ac.commandSend(f"G1 X{x} Y{y} F{self.rate}") # Going to the coordinates
            
            for j in range(self.numSteps): # Scans through the wavelengths for a given point on the sample
                if not self.worker._is_running: # Again, for the stop button
                    break
                    
                wavelength = self.startWavelength + j * step_size
                self.mono.goto(wavelength)
                time.sleep(0.5)
                
                # Update UI
                self._x = x
                self._y = y
                self.currentWavelength = wavelength
                self.xChanged.emit()
                self.yChanged.emit()
                self.waveChanged.emit()
                
                time.sleep(0.5)
        
        print("Dunzo bununzo!")
    
    @Slot()
    def stopScan(self):
        """ Function that stops the scan. Don't have a button for it yet though... """
        if self.worker:
            self.worker.stop()
            print("Stopping scan...")


    
