from .proc import _LineProcess

class CornerstoneClient:
    def __init__(self, exe_path: str):
        self.proc = _LineProcess(exe_path)

    def open(self):
        self.proc.send("open")

    def goto(self, nm: float):
        self.proc.send(f"goto {float(nm)}")

    def position(self) -> float:
        r = self.proc.send("position")  # "OK POS=###.###"
        for tok in r.split():
            if tok.startswith("POS="):
                return float(tok.split("=")[1])
        raise RuntimeError(f"bad position line: {r}")

    def open_shutter(self):
        self.proc.send("open_shutter")

    def close_shutter(self):
        self.proc.send("close_shutter")

    def close(self):
        self.proc.close()


