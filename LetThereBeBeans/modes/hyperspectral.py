# modes/hyperspectral.py
from __future__ import annotations

import os, sys, time, threading
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, filedialog, messagebox

from config import CONFIG
from clients.cornerstone_client import CornerstoneClient

# --- Detect if running as a bundled EXE (optional, keeps stdout quiet when frozen) ---
IS_FROZEN = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
if IS_FROZEN:
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')


class HyperSpectralView(ttk.Frame):
    """HyperSpectral GUI (Cornerstone spectrograph + DataMeasurer) with ttkbootstrap styling."""

    def __init__(self, parent, app=None, config=None, go_home=None):
        super().__init__(parent, padding=12)
        self.app, self.config, self.go_home = app, config or CONFIG, go_home

        # Backend
        self.mono: CornerstoneClient | None = None

        # Scan state
        self.scan_stopped = False
        self.scan_wls: list[float] = []
        self.scan_data: list[float] = []

        # Plot handles
        self.plot_fig = None
        self.plot_ax = None
        self.plot_line = None
        self.canvas_widget = None

        # --- UI ---
        self._build_header()
        self._build_left_controls()
        self._build_plot()

        # Make resizable
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    # -------------------------------------------------------------------------
    # UI BUILDERS
    # -------------------------------------------------------------------------
    def _build_header(self):
        hdr = ttk.Frame(self)
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew")
        tb.Button(hdr, text="← Back", bootstyle=SECONDARY, command=self._on_back)\
          .pack(side="left")
        ttk.Label(hdr, text="HyperSpectral", font=("Segoe UI", 16, "bold"))\
          .pack(side="left", padx=10)

        self.status = ttk.Label(hdr, text="Idle")
        self.status.pack(side="right")

    def _build_left_controls(self):
        # Scan Settings
        scan = ttk.LabelFrame(self, text="Scan Settings", padding=10)
        scan.grid(row=1, column=0, padx=10, pady=10, sticky="n")

        self.start_e = ttk.Entry(scan); self._row(scan, "Start λ (nm):", self.start_e, 0, "500")
        self.end_e   = ttk.Entry(scan); self._row(scan, "End   λ (nm):", self.end_e,   1, "520")
        self.steps_e = ttk.Entry(scan); self._row(scan, "Step Count:",    self.steps_e, 2, "20")

        self.out_e = ttk.Entry(scan, width=28); self._row(scan, "Save CSV:", self.out_e, 3)
        tb.Button(scan, text="Browse", bootstyle=INFO, command=self._pick_csv)\
          .grid(row=3, column=2, padx=4)

        btns = ttk.Frame(scan); btns.grid(row=4, column=0, columnspan=3, pady=8, sticky="ew")
        tb.Button(btns, text="Connect",  bootstyle=SUCCESS,  command=self._connect).grid(row=0, column=0, padx=4)
        tb.Button(btns, text="Start",    bootstyle=PRIMARY,  command=self._start_with_plot).grid(row=0, column=1, padx=4)
        tb.Button(btns, text="Stop",     bootstyle=DANGER,   command=self._stop_scan).grid(row=0, column=2, padx=4)
        tb.Button(btns, text="Shutdown", bootstyle=SECONDARY, command=self._shutdown).grid(row=0, column=3, padx=4)

        # Wavelength Control
        wl = ttk.LabelFrame(self, text="Wavelength Control", padding=10)
        wl.grid(row=2, column=0, padx=10, pady=10, sticky="n")

        self.wl_entry = ttk.Entry(wl); self._row(wl, "Set Wavelength:", self.wl_entry, 0, "550")
        tb.Button(wl, text="Set", bootstyle=SUCCESS, command=self._set_wavelength)\
          .grid(row=0, column=2, padx=4)

        tb.Button(wl, text="Get Wavelength", bootstyle=PRIMARY, command=self._get_wavelength)\
          .grid(row=1, column=0, columnspan=3, pady=(6, 2))

        self.lbl_current = ttk.Label(wl, text="Current Wavelength: --")
        self.lbl_current.grid(row=2, column=0, columnspan=3, sticky="w")

        # Shutter Control
        sh = ttk.LabelFrame(self, text="Shutter Control", padding=10)
        sh.grid(row=3, column=0, padx=10, pady=10, sticky="n")

        tb.Button(sh, text="Open Shutter",  bootstyle=SUCCESS, command=self._open_shutter)\
          .grid(row=0, column=0, padx=4)
        tb.Button(sh, text="Close Shutter", bootstyle=DANGER,  command=self._close_shutter)\
          .grid(row=0, column=1, padx=4)

    def _build_plot(self):
        plot = ttk.LabelFrame(self, text="Live Plot", padding=10)
        plot.grid(row=1, column=1, rowspan=3, padx=10, pady=10, sticky="nsew")
        plot.grid_columnconfigure(0, weight=1)
        plot.grid_rowconfigure(0, weight=1)

        # Initialize Matplotlib canvas
        self.plot_fig, self.plot_ax = plt.subplots()
        self.plot_line, = self.plot_ax.plot([], [], 'b-')
        self.plot_ax.set_xlabel("Wavelength (nm)")
        self.plot_ax.set_ylabel("Lock-In Amp Voltage")
        self.plot_ax.set_title("Live Data")
        self.plot_ax.grid(True)
        self.plot_fig.tight_layout()

        self.canvas_widget = FigureCanvasTkAgg(self.plot_fig, master=plot)
        self.canvas_widget.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    # -------------------------------------------------------------------------
    # UI HELPERS
    # -------------------------------------------------------------------------
    def _row(self, parent, label, entry, r, default=None):
        ttk.Label(parent, text=label).grid(row=r, column=0, sticky="e", pady=3)
        entry.grid(row=r, column=1, sticky="ew", padx=4, pady=3)
        parent.grid_columnconfigure(1, weight=1)
        if default is not None:
            entry.insert(0, default)

    def _pick_csv(self):
        p = filedialog.asksaveasfilename(defaultextension=".csv",
                                         filetypes=[("CSV files", "*.csv")])
        if p:
            self.out_e.delete(0, "end"); self.out_e.insert(0, p)

    # -------------------------------------------------------------------------
    # DEVICE COMMANDS
    # -------------------------------------------------------------------------
    def _connect(self):
        try:
            if self.mono is None:
                exe = self.config["helpers"]["cornerstone"]
                self.mono = CornerstoneClient(exe)
                self.mono.open()
            self._set_status("Cornerstone connected.")
        except Exception as e:
            messagebox.showerror("HyperSpectral", str(e))

    def _shutdown(self):
        try:
            if self.mono:
                self.mono.close()
                self.mono = None
            self._set_status("Disconnected.")
        except Exception as e:
            messagebox.showerror("HyperSpectral", str(e))

    def _set_wavelength(self):
        try:
            if not self.mono:
                raise RuntimeError("Connect Cornerstone first.")
            nm = float(self.wl_entry.get())
            self.mono.goto(nm)
            time.sleep(0.3)
            self._get_wavelength()
        except Exception as e:
            messagebox.showerror("HyperSpectral", str(e))

    def _get_wavelength(self):
        try:
            if not self.mono:
                raise RuntimeError("Connect Cornerstone first.")
            wl = self.mono.position()
            self.lbl_current.config(text=f"Current Wavelength: {wl:.3f}")
        except Exception as e:
            messagebox.showerror("HyperSpectral", str(e))

    def _open_shutter(self):
        try:
            if not self.mono: raise RuntimeError("Connect Cornerstone first.")
            self.mono.open_shutter()
            self._set_status("Shutter opened.")
        except Exception as e:
            messagebox.showerror("HyperSpectral", str(e))

    def _close_shutter(self):
        try:
            if not self.mono: raise RuntimeError("Connect Cornerstone first.")
            self.mono.close_shutter()
            self._set_status("Shutter closed.")
        except Exception as e:
            messagebox.showerror("HyperSpectral", str(e))

    # -------------------------------------------------------------------------
    # SCAN LOGIC
    # -------------------------------------------------------------------------
    def _start_with_plot(self):
        # Initialize empty plot
        self.scan_data = []
        self.scan_wls = []
        self._update_plot()
        # Run in the GUI thread using .after loop (keeps UI responsive)
        self._start_scan()

    def _start_scan(self):
        self.scan_stopped = False
        try:
            if not self.mono:
                raise RuntimeError("Connect Cornerstone first.")

            start_wl = float(self.start_e.get())
            end_wl   = float(self.end_e.get())
            steps    = int(self.steps_e.get())
            save_path = self.out_e.get().strip()
            if not save_path:
                messagebox.showerror("Input Error", "Please select a save location.")
                return

            self.scan_wls = np.linspace(start_wl, end_wl, steps + 1).tolist()
            self.scan_data = []

            # Go to start and open shutter
            self.mono.goto(start_wl)
            time.sleep(0.8)
            self.mono.open_shutter()

            # Kick off step loop
            self.after(0, lambda: self._step_loop(0, save_path))

        except ValueError:
            messagebox.showerror("Input Error", "Start/End wavelengths and steps must be numbers.")
        except Exception as e:
            messagebox.showerror("Unexpected Error", str(e))

    def _step_loop(self, index: int, save_path: str):
        if self.scan_stopped or index >= len(self.scan_wls):
            # Close shutter and save (if not stopped)
            try:
                if self.mono:
                    self.mono.close_shutter()
            finally:
                if not self.scan_stopped and len(self.scan_data) > 0:
                    arr = np.column_stack([np.array(self.scan_wls[:len(self.scan_data)]),
                                           np.array(self.scan_data)])
                    np.savetxt(save_path, arr, delimiter=",",
                               header="Wavelength,Intensity", comments='')
                    self._set_status(f"Saved: {save_path}")
            return

        wl = self.scan_wls[index]
        try:
            # Move to wavelength
            self.mono.goto(wl)
            time.sleep(0.3)

            # Measure intensity
            try:
                import DataMeasurer as dm
                intensity = dm.record()
            except Exception:
                intensity = 0.0

            self.scan_data.append(float(intensity))
            self._update_plot()
            self._set_status(f"{index+1}/{len(self.scan_wls)}  λ={wl:.2f} nm  val={intensity:.4g}")

            # Schedule next step
            self.after(100, lambda: self._step_loop(index + 1, save_path))

        except Exception as e:
            messagebox.showerror("HyperSpectral", str(e))
            # Attempt to close shutter if error
            try:
                if self.mono:
                    self.mono.close_shutter()
            except Exception:
                pass

    def _stop_scan(self):
        self.scan_stopped = True
        self._set_status("Stopping...")

    # -------------------------------------------------------------------------
    # PLOT
    # -------------------------------------------------------------------------
    def _update_plot(self):
        if self.plot_line is None:  # safety
            return
        x = np.array(self.scan_wls[:len(self.scan_data)])
        y = np.array(self.scan_data)
        self.plot_line.set_data(x, y)
        self.plot_ax.relim()
        self.plot_ax.autoscale_view()
        if self.plot_fig:
            self.plot_fig.canvas.draw_idle()

    # -------------------------------------------------------------------------
    # NAV / LIFECYCLE
    # -------------------------------------------------------------------------
    def _set_status(self, text: str):
        self.status.config(text=text)
        self.update_idletasks()

    def _on_back(self):
        self._shutdown()
        if self.go_home:
            self.go_home()

    def destroy(self):
        try:
            self._shutdown()
        finally:
            super().destroy()
