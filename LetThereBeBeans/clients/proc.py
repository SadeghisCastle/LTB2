# proc.py
import os
import subprocess

class _LineProcess:
    """
    Minimal line-oriented subprocess wrapper (stdin/stdout).
    Used for th260_helper.exe and stage_helper.exe.
    """
    def __init__(self, exe_path):
        self.exe_path = exe_path
        self.p = subprocess.Popen(
            [exe_path],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", bufsize=1
        )
        greet = self.p.stdout.readline()
        print("greet", exe_path, greet, "\n")
        if not greet.startswith("OK"):
            raise RuntimeError(f"{os.path.basename(exe_path)} not ready: {greet}")

    def send(self, line, timeout=10.0):
        self.p.stdin.write(line + "\n")
        self.p.stdin.flush()
        resp = self.p.stdout.readline()
        #print("resp", resp)
        if not resp.startswith("OK"):
            raise RuntimeError(resp)
        return resp

    def close(self):
        try:
            self.send("exit")
        except Exception:
            pass
        try:
            self.p.terminate()
        except Exception:
            pass

