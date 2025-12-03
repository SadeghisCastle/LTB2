from PySide6.QtCore import QObject, Signal, Property, Slot, QThread
from hardware_controllers import *
from cores import MasterCore, LivePlot
import os
import csv
import niscope
import numpy as np
import pyqtgraph as pg
import time
from datetime import datetime

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

class HyperSpectral(QObject):
    """ 
    Hyperspectral scanning automation.
    Coordinates XWing and Cornerstone cores to scan wavelengths at stored positions.
    """
    
    def __init__(self, xwing, cornerstone):
        super().__init__()
        # Store references to cores
        self.xwing = xwing
        self.cornerstone = cornerstone
        
        # Add automation-specific hardware
        self.digi = NIScopeClient()
        self.plotter = None  # Create when needed
        self.worker = None
        
        print("HyperSpectral automation ready")
    
    @Slot()
    def recall(self):
        """
        Start the hyperspectral scan automation.
        Tied to the recall button - will be replaced with dedicated automation GUI later.
        """
        # Make sure we can't run a scan if one is already going
        if self.worker is not None and self.worker.is_running():
            print("Hold ur horses...")
            return
        
        # Create plotter if needed
        if self.plotter is None:
            self.plotter = LivePlot()
        
        # Create the worker that will run the automation on a different thread
        self.worker = Worker(self._runScan)
        self.worker.start()
        print("Scan started")
    
    @Slot()
    def stopScan(self):
        """Stop the current scan"""
        if self.worker:
            self.worker.stop()
            print("Stopping scan...")
    
    def _runScan(self):
        """
        Automation logic - runs in separate thread.
        The underscore denotes that it doesn't interact with the GUI directly.
        """
        # Create timestamped directory for this scan
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = os.path.join("data", timestamp)
        os.makedirs(output_dir, exist_ok=True)
        csv_filename = os.path.join(output_dir, 'scan.csv')
        
        print(f"Saving data to: {output_dir}")
        
        # Calculate wavelength step size
        step_size = (self.cornerstone.endWavelength - self.cornerstone.startWavelength) / (self.cornerstone.numSteps - 1)
        
        # Open shutter
        self.cornerstone.mono.open_shutter()
        
        # Prepare data storage
        data = []
        
        # Loop through stored positions
        for i in range(len(self.xwing.coordinates)):
            if not self.worker._is_running:  # Check stop button
                break
            
            # Get coordinates from XWing
            x, y = self.xwing.coordinates[i]
            
            # Move to position
            self.xwing.ac.commandSend(f"G1 X{x} Y{y} F{self.xwing.rate}")
            print(f"Position {i+1}/{len(self.xwing.coordinates)}: X={x}, Y={y}")
            time.sleep(4)
            
            # Reset plot for new position
            self.plotter.resetPlot()
            
            # Scan through wavelengths at this position
            for j in range(self.cornerstone.numSteps):
                if not self.worker._is_running:  # Check stop button
                    break
                
                # Set wavelength
                wavelength = self.cornerstone.startWavelength + j * step_size
                self.cornerstone.mono.goto(wavelength)
                
                time.sleep(1)
                
                # Take measurement
                dataPoint = self.digi.record()
                
                # Store data
                data.append({
                    'x': x,
                    'y': y,
                    'wavelength': wavelength,
                    'intensity': dataPoint
                })
                
                # Update UI (update core states which triggers GUI updates)
                self.xwing._x = x
                self.xwing._y = y
                self.xwing.xChanged.emit()
                self.xwing.yChanged.emit()
                
                self.cornerstone.currentWavelength = wavelength
                self.cornerstone.waveChanged.emit()
                
                # Update plot
                self.plotter.updatePlot(wavelength, dataPoint)
                
                print(f"  λ={wavelength:.2f} nm, Intensity={dataPoint}")
            
            # Save to CSV after each position (crash-safe)
            with open(csv_filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['x', 'y', 'wavelength', 'intensity'])
                writer.writeheader()
                writer.writerows(data)
            
            print(f"Saved data - {len(data)} measurements")
        
        # Close shutter when done
        self.cornerstone.mono.close_shutter()
        print(f"Scan complete! Data saved to: {csv_filename}")

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
                        min_num_pts=5000000,
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

class HyperSpectralExtinction(QObject):
    """Extinction automation using hyperspectral setup"""

    def __init__(self, xwing, cornerstone):
        super().__init__()
        self.digi = NIScopeClient()
        self.plotter = None
        self.worker = None
        self.pmt = ArduinoClient("COM9", 115200)
        self.gain = 0
        self.pmt.commandSend(f"{self.gain:.3f}")
        self.xwing = xwing
        self.cornerstone = cornerstone

        print("Extinction Automation Ready")
    
    @Slot()
    def threading(self):
        """
        Start the hyperspectral scan automation.
        Tied to the recall button - will be replaced with dedicated automation GUI later.
        """
        # Make sure we can't run a scan if one is already going
        if self.worker is not None and self.worker.is_running():
            print("Hold ur horses...")
            return
        
        # Create plotter if needed
        if self.plotter is None:
            self.plotter = LivePlot()
        
        # Create the worker that will run the automation on a different thread
        self.worker = Worker(self._extinction)
        self.worker.start()
        print("Scan started")
    
    @Slot()
    def stopScan(self):
        """Stop the current scan"""
        if self.worker:
            self.worker.stop()
            print("Stopping scan...")
    
    def _extinction(self):
        """
        Automation logic - runs in separate thread.
        Includes automatic gain control to keep detector voltage in optimal range.
        """
        # Create timestamped directory for this scan
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = os.path.join("data", timestamp)
        os.makedirs(output_dir, exist_ok=True)
        csv_filename = os.path.join(output_dir, 'scan.csv')
    
        print(f"Saving data to: {output_dir}")
    
        # Calculate wavelength step size
        step_size = (self.cornerstone.endWavelength - self.cornerstone.startWavelength) / (self.cornerstone.numSteps - 1)
    
        # Open shutter
        self.cornerstone.mono.open_shutter()
    
        # Prepare data storage
        data = []
    
        # Gain control parameters
        TARGET_VOLTAGE = 8.0  # Middle of 4-12V range
        VOLTAGE_MIN = 4.0
        VOLTAGE_MAX = 12.0
        MAX_GAIN_ADJUSTMENTS = 20  # Prevent infinite loops
    
        # Loop through stored positions
        for i in range(len(self.xwing.coordinates)):
            if not self.worker._is_running:
                break
        
            x, y = self.xwing.coordinates[i]
        
            # Move to position
            self.xwing.ac.commandSend(f"G1 X{x} Y{y} F{self.xwing.rate}")
            print(f"Position {i+1}/{len(self.xwing.coordinates)}: X={x}, Y={y}")
            time.sleep(4)
        
            # Reset plot for new position
            self.plotter.resetPlot()
        
            # Scan through wavelengths at this position
            for j in range(self.cornerstone.numSteps):
                if not self.worker._is_running:
                    break
            
                # Set wavelength
                wavelength = self.cornerstone.startWavelength + j * step_size
                self.cornerstone.mono.goto(wavelength)
            
                # Wait for wavelength to stabilize (with workaround for stuck -1)
                while self.cornerstone.mono.position() == -1:
                    self.cornerstone.mono.goto(wavelength)  # Workaround for bug
                    time.sleep(0.1)
            
                time.sleep(1)
            
                # Automatic gain control
                dataPoint = self.digi.record()
                adjustment_count = 0
            
                while (dataPoint < VOLTAGE_MIN or dataPoint > VOLTAGE_MAX) and adjustment_count < MAX_GAIN_ADJUSTMENTS:
                    if dataPoint > VOLTAGE_MAX:
                        # Voltage too high - reduce gain
                        step = 0.1 if abs(dataPoint - TARGET_VOLTAGE) > 2 else 0.01
                        self.gain -= step
                        print(f"    Voltage {dataPoint:.2f}V too high, reducing gain to {self.gain:.3f}")
                    
                    elif dataPoint < VOLTAGE_MIN:
                        # Voltage too low - increase gain
                        step = 0.1 if abs(dataPoint - TARGET_VOLTAGE) > 2 else 0.01
                        self.gain += step
                        print(f"    Voltage {dataPoint:.2f}V too low, increasing gain to {self.gain:.3f}")
                
                    # Apply new gain
                    self.pmt.commandSend(f"{self.gain:.3f}")
                    time.sleep(1)
                
                    # Take new measurement
                    dataPoint = self.digi.record()
                    adjustment_count += 1
            
                if adjustment_count >= MAX_GAIN_ADJUSTMENTS:
                    print(f"    Warning: Could not stabilize voltage after {MAX_GAIN_ADJUSTMENTS} attempts")
            
                # Store data (including gain used)
                data.append({
                    'x': x,
                    'y': y,
                    'wavelength': wavelength,
                    'intensity': dataPoint,
                    'gain': self.gain  # Record gain used for this measurement
                })
            
                # Update UI
                self.xwing._x = x
                self.xwing._y = y
                self.xwing.xChanged.emit()
                self.xwing.yChanged.emit()
            
                self.cornerstone.currentWavelength = wavelength
                self.cornerstone.waveChanged.emit()
            
                # Update plot
                self.plotter.updatePlot(wavelength, dataPoint)
            
                print(f"  λ={wavelength:.2f} nm, Voltage={dataPoint:.2f}V, Gain={self.gain:.3f}")
        
            # Save to CSV after each position (crash-safe)
            with open(csv_filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['x', 'y', 'wavelength', 'intensity', 'gain'])
                writer.writeheader()
                writer.writerows(data)
        
            print(f"Saved data - {len(data)} measurements")
    
        # Close shutter when done
        self.cornerstone.mono.close_shutter()
        print(f"Scan complete! Data saved to: {csv_filename}")

class QuickScanAutomation(QObject):
    """Different automation using same cores"""
    
    def __init__(self, xwing, cornerstone):
        super().__init__()
        self.pmt = ArduinoClient("COM9", 115200)

    @Slot()
    def threading(self):
        if self.worker is not None and self.worker._is_running():
            print("Hold ur horses...")
            return
        
        # Create the object that will run the automation on a different thread
        self.worker = Worker(self._extinction)
        self.worker.start()
        print("Scan started")
    
    @Slot()
    def _extinction(self):
        voltages = np.linspace(0, 1, 11)

        for i in range(len(voltages)):
            self.pmt.commandSend(f"{voltages[i]:.3f}")
            print(voltages[i])
            time.sleep(1)
    
