# stepper_arrows_min.py
# Keyboard ← / → to move X by a fixed step (absolute G-code)
# H = Home (X0), 0 = Set Zero (G92), S = Stop

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox

# --- import your client (adjust path if needed) ---
from pathlib import Path
import sys
HERE = Path(__file__).resolve()
ROOT = HERE.parent.parent          
CLIENTS_DIR = ROOT / "clients"
sys.path.insert(0, str(CLIENTS_DIR))
import arduino_client as AC      # <-- your renamed module

# --- optional: auto-pick CH340 (your Arduino clone) ---
import serial.tools.list_ports
CH340_VID, CH340_PID = 0x1A86, 0x7523
def find_ch340_port():
    for p in serial.tools.list_ports.comports():
        if p.vid == CH340_VID and p.pid == CH340_PID:
            return p.device
    for p in serial.tools.list_ports.comports():
        if "CH340" in (p.description or "").upper():
            return p.device
    return None

DEFAULT_BAUD = 115200

class App(tb.Window):
    def __init__(self):
        super().__init__(title="Stepper Arrows (X axis)", themename="flatly")
        self.geometry("340x170")
        self.resizable(False, False)

        self.dev = None
        self.x_pos  = tk.DoubleVar(value=0.0)   # absolute X (mm) we command
        self.step   = tk.DoubleVar(value=1.0)   # mm per arrow press
        self.feed   = tk.IntVar(value=300)      # mm/min
        self.port   = tk.StringVar(value=find_ch340_port() or "COM4")
        self.baud   = tk.IntVar(value=DEFAULT_BAUD)

        self._build()
        self._bind_keys()
        self._set_connected(False)

    def _build(self):
        pad = 8
        top = tb.Frame(self, padding=pad); top.pack(fill=tk.X)
        tb.Entry(top, textvariable=self.port, width=10).grid(row=0, column=0, padx=(0,6))
        tb.Entry(top, textvariable=self.baud, width=8).grid(row=0, column=1, padx=(0,6))
        self.btn_conn = tb.Button(top, text="Connect", bootstyle="success", command=self.connect)
        self.btn_disc = tb.Button(top, text="Disconnect", bootstyle="secondary-outline", command=self.disconnect)
        self.btn_conn.grid(row=0, column=2); self.btn_disc.grid(row=0, column=3, padx=(6,0))

        mid = tb.Frame(self, padding=pad); mid.pack(fill=tk.X)
        tb.Label(mid, text="Step (mm)").grid(row=0, column=0, sticky="w")
        tb.Spinbox(mid, from_=0.001, to=1000, increment=0.1, format="%.3f",
                   textvariable=self.step, width=8).grid(row=0, column=1, padx=(4,12))
        tb.Label(mid, text="Feed (mm/min)").grid(row=0, column=2, sticky="w")
        tb.Spinbox(mid, from_=1, to=60000, increment=10,
                   textvariable=self.feed, width=8).grid(row=0, column=3, padx=(4,0))

        arrows = tb.Frame(self, padding=(pad,0)); arrows.pack()
        tb.Button(arrows, text="←", width=8, command=lambda: self.nudge(-1)).grid(row=0, column=0, padx=6)
        tb.Button(arrows, text="⏹", width=6, bootstyle="danger", command=self.stop).grid(row=0, column=1, padx=6)
        tb.Button(arrows, text="→", width=8, command=lambda: self.nudge(+1)).grid(row=0, column=2, padx=6)

        bottom = tb.Frame(self, padding=(pad, pad, pad, pad)); bottom.pack(fill=tk.X)
        tb.Button(bottom, text="Home (H)", bootstyle="info", command=self.home).pack(side=tk.LEFT)
        tb.Button(bottom, text="Zero (0)", bootstyle="secondary", command=self.set_zero).pack(side=tk.LEFT, padx=6)
        self.lbl = tb.Label(bottom, text=self._pos_text(), bootstyle="secondary")
        self.lbl.pack(side=tk.RIGHT)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _bind_keys(self):
        # focus the window and use OS key-repeat for continuous nudging
        self.bind("<Left>",  lambda e: self.nudge(-1))
        self.bind("<Right>", lambda e: self.nudge(+1))
        self.bind("h",       lambda e: self.home())
        self.bind("s",       lambda e: self.stop())
        self.bind("0",       lambda e: self.set_zero())

    def _pos_text(self): return f"X = {self.x_pos.get():.3f} mm"

    # ---- serial ----
    def connect(self):
        try:
            self.dev = AC.serialInit(self.port.get().strip(), int(self.baud.get()))
            # define zero on connect to align UI with controller
            AC.commandSend(self.dev, "G92 X0", int(self.baud.get()))
            self.x_pos.set(0.0); self.lbl.configure(text=self._pos_text())
            self._set_connected(True)
        except Exception as e:
            Messagebox.show_error(f"Connect failed: {e}")

    def disconnect(self):
        try:
            if self.dev: AC.serialClose(self.dev)
        finally:
            self.dev = None; self._set_connected(False)

    def _set_connected(self, ok):
        self.btn_conn.configure(state=(tk.DISABLED if ok else tk.NORMAL))
        self.btn_disc.configure(state=(tk.NORMAL if ok else tk.DISABLED))

    # ---- moves ----
    def _send(self, cmd: str):
        try:
            AC.commandSend(self.dev, cmd, int(self.baud.get()))
        except Exception as e:
            Messagebox.show_error(f"Command failed:\n{cmd}\n\n{e}")

    def nudge(self, sign: int):
        if not self.dev: return Messagebox.show_warning("Not connected")
        self.x_pos.set(self.x_pos.get() + sign * float(self.step.get()))
        self.lbl.configure(text=self._pos_text())
        self._send(f"G1 X{self.x_pos.get():.3f} F{int(self.feed.get())}")

    def home(self):
        if not self.dev: return Messagebox.show_warning("Not connected")
        self.x_pos.set(0.0); self.lbl.configure(text=self._pos_text())
        self._send(f"G1 X0 F{int(self.feed.get())}")

    def set_zero(self):
        if not self.dev: return Messagebox.show_warning("Not connected")
        self._send("G92 X0")
        self.x_pos.set(0.0); self.lbl.configure(text=self._pos_text())

    def stop(self):
        if not self.dev: return
        # change this if your firmware uses a different hold/pause
        self._send("M0")

    def _on_close(self):
        try:
            if self.dev: AC.serialClose(self.dev)
        finally:
            self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
