# LTB2 Guide

## 0) What this app is

A Python GUI that controls lab hardware:

* Cornerstone monochromator (via `cornerstone_helper.exe`)
* Thorlabs KCube Piezo stage (via `stage_helper.exe`)
* PicoQuant TimeHarp TH260 TCSPC board (via `th260_helper.exe`)

It has multiple modes (screens). Each mode is a workflow combining one or more devices:

* **HyperSpectral** (example below): sweeps the monochromator across wavelengths and records data.
* **FLIM**: performs stage scanning and TH260 acquisitions.
* More can be added in the future.

The Python GUI talks to small helper EXEs using a simple **line protocol** (text in/out). This keeps the GUI stable and makes it easy to add new hardware later.

---

## 1) Folder layout

```text
your_app/
  main.py                         # app bootstrap + home menu
  config.py                       # where helper EXEs live (paths)
  requirements.txt                # pip dependencies

  clients/                        # thin Python wrappers for helpers
    proc.py
    cornerstone_client.py
    stage_client.py
    th260_client.py
    # add more clients here

  modes/                          # GUI screens
    hyperspectral.py
    flim.py
    # add more modes here

  helpers/                        # helper EXEs (compiled elsewhere)
    cornerstone_helper.exe
    stage_helper.exe
    th260_helper.exe
    # add more helpers here
```

---

## 2) Install (Windows)

* Install **Python (64‑bit)**
* Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 3) Configure helper EXEs

Check `config.py` to make sure the paths point to your helper executables:

```python
# config.py
CONFIG = {
    "helpers": {
        "cornerstone": r"helpers\cornerstone_helper.exe",
        "stage":       r"helpers\stage_helper.exe",
        "th260":       r"helpers\th260_helper.exe",
    }
}
```

---

## 4) Run the app

* You’ll see the **Home** screen with buttons for each available mode.
* Pick a mode → that screen opens with its own controls.

**Example: HyperSpectral mode**

1. **Connect** → initializes the Cornerstone helper.
2. Enter **start/end wavelengths** and a **step count**.
3. Pick a **CSV save path**.
4. **Start** → moves the monochromator, records intensity values, plots them live, and saves them to CSV.

Other modes (like **FLIM**) follow the same pattern:

> connect → enter parameters → start → data collection → save

---

## 5) Test without hardware (SIM mode)

Run the app in **simulation mode**:

**Cmd.exe**

```bat
set HYPER_SIM=1
python main.py
```

**PowerShell**

```powershell
$env:HYPER_SIM="1"; python .\main.py
```

**What happens in SIM:**

* **Cornerstone**: `goto`, `position`, `open_shutter` are faked.
* **Stage**: `open`, `move_ix`, etc. are faked.
* **TH260**: `measure` writes fake histogram text files.

This lets you test the full GUI and workflow without lab hardware.

---

## 6) Add a new mode

1. Create a new file in `modes/` (e.g. `autoscan.py`).
2. Make a view class (`AutoScanView`) that builds a GUI and uses one or more clients.
3. Register the new mode in `main.py` so it shows up on the home screen.

---

## 7) Key ideas to remember

* **Helpers** = tiny EXEs that talk to hardware.
* **Clients** = Python classes that hide the text protocol.
* **Modes** = GUI workflows that combine clients.
* **Simulator** = fakes all devices (`HYPER_SIM=1`).

---

# Add a New Device — Step‑by‑Step

## Overview

You’ll create a tiny **helper program (EXE)** that controls the hardware and talks over a line protocol (plain text). Our Python GUI never calls vendor DLLs directly—it just sends commands like `open`, `status`, `set gain=10`, `capture "C:\\file.tif"` and reads replies like `OK ...` or `ERR ...`.

This keeps the GUI simple and makes devices **plug‑in** modules.

---

## 1) Prototype the hardware control

First, forget the GUI. Get any code to talk to the device and do one or two actions you care about (e.g., open device, set a parameter, take a measurement).

Pick the language that’s easiest for your device:

* If the vendor has a **Python SDK**: use Python (easiest to prototype).
* If they provide **.NET DLLs**: write a C# console app.
* If only **C/C++ SDK** or plain DLL: write a C++ console app.

The goal here is just to prove you can command the device and get a result.

**Example (Python) — minimal “device control”**

```python
# prototype_camera.py (example)
import time

def open_device():
    # TODO: call vendor SDK to open
    print("opened")

def set_exposure(ms):
    # TODO
    print(f"exposure={ms}ms set")

def capture(path):
    # TODO: acquire and save to 'path'
    print(f"captured -> {path}")

if __name__ == "__main__":
    open_device()
    set_exposure(50)
    capture("C:/temp/test.tif")
```

---

## 2) Wrap your prototype as a helper EXE

Turn your working code into a tiny console app that:

* Reads **one line** from `stdin`.
* Executes the matching action.
* Writes **one line back**:

  * `OK ...` on success
  * `ERR <message>` on failure
* Loops until exit.

**Python helper template (drop‑in)**

> This runs without vendor code; replace the TODOs with your SDK calls later.

```python
# helper_camera.py
import sys, shlex, time, os

def println(s): sys.stdout.write(s + "\n"); sys.stdout.flush()

class Camera:
    def __init__(self):
        self.opened = False
        self.exposure_ms = 50

    def open(self):
        # TODO: open via vendor API
        self.opened = True

    def status(self):
        # Add any fields you like as key=value pairs
        return f"ready={int(self.opened)} exposure_ms={self.exposure_ms}"

    def set_exposure(self, ms:int):
        # TODO
        self.exposure_ms = ms

    def capture(self, path:str):
        # TODO: real acquisition; for now, make a dummy file
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("FAKE_IMAGE\n")

def main():
    cam = Camera()
    println("OK ready")  # greeting (our clients expect an initial OK)

    for raw in sys.stdin:
        line = raw.strip()
        if not line:
            println("OK"); continue
        try:
            # Support quoted paths: capture "C:\\with spaces\\file.tif"
            parts = shlex.split(line)
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd == "open":
                cam.open(); println("OK")
            elif cmd == "status":
                println("OK " + cam.status())
            elif cmd == "set":
                # syntax: set key=value
                kv = args[0]
                key, val = kv.split("=", 1)
                if key == "exposure":
                    cam.set_exposure(int(val))
                    println("OK")
                else:
                    println("ERR unknown_param")
            elif cmd == "capture":
                # capture "C:/path/file.tif"
                path = args[0]
                cam.capture(path)
                println("OK")
            elif cmd == "exit":
                println("OK bye")
                break
            else:
                println("ERR unknown_cmd")
        except Exception as e:
            println(f"ERR {e}")

if __name__ == "__main__":
    main()
```

**Package the helper as an EXE (Windows)**

Using **PyInstaller** (already in your requirements):

```bash
pyinstaller --noconfirm --onefile --console helper_camera.py
```

You’ll get `dist/helper_camera.exe`. Put it in your app’s `helpers/` folder.

---

## 3) Register the helper in `config.py`

Tell the app where your helper EXE lives:

```python
# config.py
CONFIG = {
    "helpers": {
        "cornerstone": r"helpers\cornerstone_helper.exe",
        "stage":       r"helpers\stage_helper.exe",
        "th260":       r"helpers\th260_helper.exe",
        "camera":      r"helpers\helper_camera.exe",   # ← new device
    }
}
```

---

## 4) Create a client (thin Python wrapper)

Clients hide the text protocol behind nice methods.

```python
# clients/camera_client.py
from .proc import LineProcess  # already handles real vs simulator

class CameraClient:
    def __init__(self, exe_path: str):
        self.proc = LineProcess(exe_path)

    def open(self):
        self.proc.send_ok("open")

    def status(self) -> dict:
        # expects: "OK key=a value=b"
        s = self.proc.send_ok("status")
        parts = s.split()[1:]  # drop "OK"
        return dict(p.split("=", 1) for p in parts if "=" in p)

    def set_exposure(self, ms: int):
        self.proc.send_ok(f"set exposure={ms}")

    def capture(self, out_path: str):
        # quote the path to allow spaces
        self.proc.send_ok(f'capture "{out_path}"')

    def close(self):
        self.proc.close()
```

---

## 5) Use it in a mode (or any Python code)

```python
from config import CONFIG
from clients.camera_client import CameraClient

cam = CameraClient(CONFIG["helpers"]["camera"])
cam.open()
cam.set_exposure(50)
print("Status:", cam.status())
cam.capture(r"C:\\data\\img_001.tif")
cam.close()
```
