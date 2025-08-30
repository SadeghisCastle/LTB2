# modes/flim.py
import os
import time
import threading
import numpy as np
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, filedialog, messagebox

from config import CONFIG
from clients.stage_client import StageClient
from clients.th260_client import TH260Client
from clients.cornerstone_client import CornerstoneClient

# Fixed max output voltage for KCube Piezo in tenths of a volt (e.g., 750 = 7.50 V)
FIXED_VMAX_TENTHS = 750

class FlimView(ttk.Frame):
    def __init__(self, parent, app=None, config=None, go_home=None):
        super().__init__(parent, padding=12)
        self.app, self.config, self.go_home = app, config or CONFIG, go_home
        self.stage = None
        self.th260 = None
        self.mono  = None
        self.stop_flag = False
        self.worker = None

        # Header
        hdr = ttk.Frame(self); hdr.pack(fill="x")
        tb.Button(hdr, text="← Back", bootstyle=SECONDARY, command=self._back).pack(side="left")
        ttk.Label(hdr, text="FLIM", font=("Segoe UI", 16, "bold")).pack(side="left", padx=10)

        # Config panel (no Vmax input; fixed)
        left = ttk.LabelFrame(self, text="Config", padding=10)
        left.pack(side="left", fill="y", padx=10, pady=10)

        self.width_e  = ttk.Entry(left);  self._row(left, "Width (px):",  self.width_e,  0, "5")
        self.height_e = ttk.Entry(left);  self._row(left, "Height (px):", self.height_e, 1, "5")

        # Wavelengths as Start/End/Steps (like HyperSpectral)
        self.wl_start_e = ttk.Entry(left); self._row(left, "Start λ (nm):", self.wl_start_e, 2, "500")
        self.wl_end_e   = ttk.Entry(left); self._row(left, "End   λ (nm):", self.wl_end_e,   3, "520")
        self.wl_steps_e = ttk.Entry(left); self._row(left, "Steps:",         self.wl_steps_e, 4, "3")

        self.tacq_e   = ttk.Entry(left);  self._row(left, "Tacq (ms):",   self.tacq_e,   5, "1000")

        self.out_e = ttk.Entry(left, width=30); self._row(left, "Output folder:", self.out_e, 6)
        tb.Button(left, text="Browse", bootstyle=INFO, command=self._pick_dir).grid(row=6, column=2, padx=4)

        btns = ttk.Frame(left); btns.grid(row=7, column=0, columnspan=3, pady=8, sticky="ew")
        tb.Button(btns, text="Connect",    bootstyle=SUCCESS,   command=self._connect).grid(row=0, column=0, padx=4)
        tb.Button(btns, text="Disconnect", bootstyle=SECONDARY, command=self._disconnect).grid(row=0, column=1, padx=4)
        tb.Button(btns, text="Start",      bootstyle=PRIMARY,   command=self._start).grid(row=0, column=2, padx=4)
        tb.Button(btns, text="Stop",       bootstyle=DANGER,    command=self._stop).grid(row=0, column=3, padx=4)

        # Status panel
        right = ttk.LabelFrame(self, text="Status", padding=10)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.status = ttk.Label(right, text="Idle"); self.status.pack(anchor="w")

    # --- UI helpers
    def _row(self, parent, label, entry, r, default=None):
        ttk.Label(parent, text=label).grid(row=r, column=0, sticky="e", pady=3)
        entry.grid(row=r, column=1, sticky="ew", padx=4, pady=3)
        parent.grid_columnconfigure(1, weight=1)
        if default is not None: entry.insert(0, default)

    def _pick_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.out_e.delete(0, "end"); self.out_e.insert(0, d)

    # --- Device lifecycle
    def _connect(self):
        try:
            if self.stage is None:
                self.stage = StageClient(self.config["helpers"]["stage"])
                # Use fixed vmax
                self.stage.open(vmax_tenths=FIXED_VMAX_TENTHS)
            if self.th260 is None:
                self.th260 = TH260Client(self.config["helpers"]["th260"])
                # Keep compatibility with your helper's expectations
                self.th260.connect(output_dir="dump", ix=1, iy=1)
            if self.mono is None:
                self.mono = CornerstoneClient(self.config["helpers"]["cornerstone"])
                self.mono.open()
            self.status.config(text=f"Connected. Stage vmax={FIXED_VMAX_TENTHS/100:.2f} V")
        except Exception as e:
            messagebox.showerror("Connect", str(e))

    def _disconnect(self):
        try:
            if self.stage: self.stage.close()
            if self.th260: self.th260.close()
            if self.mono:  self.mono.close()
            self.status.config(text="Disconnected.")
        finally:
            self.stage = self.th260 = self.mono = None

    # --- Scan orchestration
    def _start(self):
        if not (self.stage and self.th260 and self.mono):
            messagebox.showerror("FLIM", "Connect devices first.")
            return
        try:
            W = int(self.width_e.get()); H = int(self.height_e.get())
            s = float(self.wl_start_e.get()); e = float(self.wl_end_e.get()); steps = int(self.wl_steps_e.get())
            wls = np.linspace(s, e, steps + 1).tolist()
            tacq = int(self.tacq_e.get())
            out = self.out_e.get().strip()
            if not out: raise ValueError("Please choose an output folder.")
            os.makedirs(out, exist_ok=True)

            self.stop_flag = False
            if self.worker and self.worker.is_alive():
                messagebox.showinfo("FLIM", "A scan is already running.")
                return
            self.worker = threading.Thread(target=self._run_scan, args=(W,H,wls,tacq,out), daemon=True)
            self.worker.start()
            self.status.config(text=f"Running... λ from {s:.2f} to {e:.2f} in {steps} steps")
        except Exception as e:
            messagebox.showerror("FLIM", str(e))

    def _run_scan(self, W, H, wls, tacq, out):
        try:
            for iy in range(H):
                for ix in range(W):
                    if self.stop_flag: raise KeyboardInterrupt()
                    self.stage.move_ix(ix, iy, W, H)
                    time.sleep(0.1)

                    for nm in wls:
                        if self.stop_flag: raise KeyboardInterrupt()
                        self.mono.goto(nm)
                        time.sleep(0.8)  # settle
                        self.th260.acquire(tacq_ms=tacq, output_dir=out, wl=nm, ix=ix, iy=iy)
                        self._post_status(f"({iy+1}/{H}, {ix+1}/{W}) λ={nm:.2f} nm  tacq={tacq} ms")
            self._post_status("Done.")
        except KeyboardInterrupt:
            self._post_status("Stopped.")
        except Exception as e:
            self._post_status(f"Error: {e}")

    def _post_status(self, text):
        self.after(0, lambda: self.status.config(text=text))

    def _stop(self):
        self.stop_flag = True

    def _back(self):
        self._stop()
        self._disconnect()
        if self.go_home: self.go_home()

    def destroy(self):
        try:
            self._stop()
            self._disconnect()
        finally:
            super().destroy()
