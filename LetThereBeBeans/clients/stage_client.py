# stage_client.py
from __future__ import annotations

# Import your minimal line-based IPC helper
# If this file sits in the same 'clients' package as proc.py, use the relative import:
from .proc import _LineProcess
# If it's not in a package, change to: from proc import _LineProcess


class StageClient:
    """Wrapper for stage_helper.exe (dynamic-loaded Kinesis, serials hardcoded in the EXE)"""
    def __init__(self, exe):
        self.proc = _LineProcess(exe)

    def open(self, serial_x=None, serial_y=None, vmax_tenths=750):
        # If no serials given, the helper uses its hardcoded defaults
        if serial_x and serial_y:
            self.proc.send(f"open {serial_x} {serial_y} {vmax_tenths}")
        else:
            self.proc.send(f"open {vmax_tenths}")

    def move_ix(self, ix, iy, width, height):
        self.proc.send(f"move_ix {ix} {iy} {width} {height}")

    def reset(self, ix, width):
        self.proc.send(f"stage_reset {ix} {width}")

    def setdac(self, vx_code, vy_code):
        self.proc.send(f"setdac {vx_code} {vy_code}")

    def status(self):
        r = self.proc.send("status")
        # r: "OK X=<0|1> Y=<0|1>"
        return dict(kv.split("=") for kv in r[3:].split())

    def disable(self):
        try:
            self.proc.send("disable")
        except Exception:
            pass

    def close(self):
        try:
            self.disable()
        finally:
            self.proc.close()
