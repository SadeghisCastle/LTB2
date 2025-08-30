# main.py
import importlib
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk
from config import CONFIG

MODES = {
    "HyperSpectral": "modes.hyperspectral:HyperSpectralView",  # ← renamed
    "FLIM": "modes.flim:FlimView",
}

class App(tb.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Let There Be Beans")
        self.geometry("1200x700")

        self.container = ttk.Frame(self)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.current_view = None
        self.show_home()

    def show_home(self):
        self._clear_view()
        self.current_view = HomeView(self.container, self)
        self.current_view.grid(row=0, column=0, sticky="nsew")

    def show_mode(self, spec: str):
        self._clear_view()
        module_name, class_name = spec.split(":")
        mod = importlib.import_module(module_name)
        ViewClass = getattr(mod, class_name)
        self.current_view = ViewClass(self.container, app=self, config=CONFIG, go_home=self.show_home)
        self.current_view.grid(row=0, column=0, sticky="nsew")

    def _clear_view(self):
        if self.current_view is not None:
            try:
                self.current_view.destroy()
            finally:
                self.current_view = None

class HomeView(ttk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, padding=20)

        # Expand outer rows/cols
        for r in (0, 2):
            self.grid_rowconfigure(r, weight=1)
        for c in (0, 2):
            self.grid_columnconfigure(c, weight=1)

        # Center cell
        center = ttk.Frame(self)
        center.grid(row=1, column=1)

        ttk.Label(center, text="Select a Mode", font=("Segoe UI", 18, "bold")).pack(pady=(0, 12))

        for label, spec in MODES.items():
            tb.Button(
                center,
                text=label,
                bootstyle=PRIMARY,
                width=32,
                command=lambda s=spec: app.show_mode(s)
            ).pack(pady=6, fill="x")




if __name__ == "__main__":
    App().mainloop()
