from PySide6.QtCore import QObject, Signal, Property, Slot, QThread
from hardware_controllers import *
from cores import MasterCore, LivePlot
import os
import csv

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

class HyperSpectral(MasterCore):
    """ First automation. We can create the required objects from cores.py and 
    use them in this new object. We aren't using functions from them, but when the code executes a command, 
    it will search through the objects that we initialize until it finds one that fits. """

    def __init__(self):
        super().__init__()
        self.digi = NIScopeClient() # Including digitizer here since we don't have a core for it yet
        self.plotter = LivePlot()
        self.worker = None

    @Slot()
    def recall(self):
        # Can use this for future automations!!!!!!!
        """ Function that ties the button to the automation logic. Using the recall button
        as a stand in until we make a gui for starting the automation """

        # Make sure we can't run a scan if one is already going
        if self.worker is not None and self.worker.isRunning():
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
        data = []

        # Select save location
        output_dir = getattr(self, 'save_directory', 'scan_data')
        os.makedirs(output_dir, exist_ok=True)
        csv_filename = os.path.join(output_dir, f'scan.csv')

        for i in range(len(self.coordinates)): # Goes through stored positions
            if not self.worker._is_running: # How the stop button actually stops the automation
                break
                
            x, y = self.coordinates[i] # Gets coordinates that are stored from X-Wing
            self.ac.commandSend(f"G1 X{x} Y{y} F{self.rate}") # Going to the coordinates
            time.sleep(4)

            self.plotter.resetPlot()

            for j in range(self.numSteps): # Scans through the wavelengths for a given point on the sample
                if not self.worker._is_running: # Again, for the stop button
                    break
                    
                wavelength = self.startWavelength + j * step_size
                self.mono.goto(wavelength)
                time.sleep(2)
                
                dataPoint = self.digi.record() # Take measurement
                data.append({
                    'x': x,
                    'y': y,
                    'wavelength': wavelength,
                    'intensity': dataPoint
                    })

                # Update UI
                self._x = x
                self._y = y
                self.currentWavelength = wavelength
                self.xChanged.emit()
                self.yChanged.emit()
                self.waveChanged.emit()

                self.plotter.updatePlot(wavelength, dataPoint)

            # Saves to csv at every position incase of error
            with open(csv_filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['x', 'y', 'wavelength', 'intensity'])
                writer.writeheader()
                writer.writerows(data)
                
        self.mono.close_shutter()
        print("Dunzo bununzo!")
    
    @Slot()
    def stopScan(self):
        """ Function that stops the scan. Don't have a button for it yet though... """
        if self.worker:
            self.worker.stop()
            print("Stopping scan...")


    
