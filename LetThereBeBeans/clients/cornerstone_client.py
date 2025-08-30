from .proc import _LineProcess

class CornerstoneClient:
    def __init__(self, exe_path: str):
        self.proc = LineProcess(exe_path)

    def open(self):
        self.proc.send_ok("open")

    def goto(self, nm: float):
        self.proc.send_ok(f"goto {float(nm)}")

    def position(self) -> float:
        r = self.proc.send_ok("position")  # "OK POS=###.###"
        for tok in r.split():
            if tok.startswith("POS="):
                return float(tok.split("=")[1])
        raise RuntimeError(f"bad position line: {r}")

    def open_shutter(self):
        self.proc.send_ok("open_shutter")

    def close_shutter(self):
        self.proc.send_ok("close_shutter")

    def close(self):
        self.proc.close()


