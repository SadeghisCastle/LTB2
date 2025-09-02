from pathlib import Path
ROOT = Path(__file__).parent.resolve()
HELPERS = ROOT / "helpers"

CONFIG = {
    "helpers": {
        "stage": str(HELPERS / "stage_helper_ultra.exe"),
        "th260": str(HELPERS / "th260_helper_ultra.exe"),
        "cornerstone": str(HELPERS / "cornerstone_helper.exe"),  # ← new name
    },
    "paths": {
        "default_output": str((ROOT / "data").resolve()),
    }
}

