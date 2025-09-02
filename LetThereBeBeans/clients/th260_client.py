# th260_client.py
from __future__ import annotations
from .proc import _LineProcess  # if this file sits in the same 'clients' package

class TH260Client:
    """
    Thin wrapper around th260_helper.exe using the shared LineProcess.
    Protocol (as implemented by your helper):
      - init <outDir> <ix> <iy>
      - measure <outDir> <ix> <iy> <wavelength_nm> <tacq_ms>
      - info            (optional; returns OK RES=... CH=... LEN=...)
      - exit
    """

    def __init__(self, exe: str):
        self.proc = _LineProcess(exe)

    # -- Setup / connection ----------------------------------------------------

    def init(self, output_dir: str, ix: int, iy: int) -> None:
        """Initialize helper with an output directory and starting pixel coords."""
        self.proc.send(f"init {output_dir} {int(ix)} {int(iy)}", timeout=20.0)

    def connect(self, output_dir: str = "dump", ix: int = 1, iy: int = 1) -> None:
        """
        Convenience: some code paths used a 'connect' that just called `init dump 1 1`.
        Keep that behavior for compatibility.
        """
        self.init(output_dir, ix, iy)

    # -- Acquisition -----------------------------------------------------------

    def acquire(self, tacq_ms: int, output_dir: str, wl: int, ix: int, iy: int) -> None:
        """
        Trigger a measurement. The helper writes data to disk in output_dir.
        We just ensure the call succeeds (OK) and wait long enough.
        """
        cmd = f"measure {output_dir} {int(ix)} {int(iy)} {int(wl)} {int(tacq_ms)}"
        # Acquisition time affects how long the helper runs; add a cushion.
        timeout = max(10.0, tacq_ms / 1000.0 + 10.0)
        self.proc.send(cmd, timeout=timeout)

    # -- Optional helpers ------------------------------------------------------

    def info(self) -> dict:
        """
        Ask the helper for instrument info if it supports `info`.
        Expected line: 'OK RES=<ps> CH=<n> LEN=<bins>'
        """
        resp = self.proc.send("info")
        parts = resp.split()[1:]  # drop 'OK'
        try:
            kv = dict(p.split("=", 1) for p in parts)
            return {
                "resolution_ps": float(kv.get("RES", "0")),
                "channels": int(kv.get("CH", "0")),
                "bins": int(kv.get("LEN", "0")),
            }
        except Exception:
            # If helper doesn't support info or format differs, return raw text
            return {"raw": resp}

    # -- Shutdown --------------------------------------------------------------

    def close(self) -> None:
        """Gracefully stop the helper process."""
        self.proc.close()
