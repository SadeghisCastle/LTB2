import importlib
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk

MODES = {
    "HyperSpectral": "modes.hyperspectral:HyperSpectralView",
    "FLIM": "modes.flim:FlimView",
}

class App(tb.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Let There Be Beans")
        self.geometry("1200x700")

        # Root expands
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Container expands
        self.container = ttk.Frame(self)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.current_view = None
        self.show_home()

        self.after(0, self._center_on_screen)

    def _center_on_screen(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def show_home(self):
        self._clear_view()
        def _show():
            self.current_view = HomeView(self.container, self)
            self.current_view.grid(row=0, column=0, sticky="nsew")
        self.after(0, _show)


    def show_mode(self, spec: str):
        self._clear_view()
        module_name, class_name = spec.split(":")
        mod = importlib.import_module(module_name)
        ViewClass = getattr(mod, class_name)
        self.current_view = ViewClass(self.container, app=self, config=None, go_home=self.show_home)
        self.current_view.grid(row=0, column=0, sticky="nsew")

    def _clear_view(self):
        if self.current_view is not None:
            try:
                self.current_view.destroy()
            finally:
                self.current_view = None


class HomeView(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=0)

        # Outer 3x3 spacer grid to center the block
        for r in (0, 2):
            self.grid_rowconfigure(r, weight=1)
        for c in (0, 2):
            self.grid_columnconfigure(c, weight=1)

        # Middle cell holds the menu block
        center = ttk.Frame(self, padding=20)
        center.grid(row=1, column=1)

        center.grid_columnconfigure(0, weight=1)

        ttk.Label(
            center,
            text="Select a Mode",
            font=("Segoe UI", 18, "bold"),
            anchor="center",
        ).grid(row=0, column=0, pady=(0, 12), sticky="ew")

        row = 1
        for label, spec in MODES.items():
            tb.Button(
                center,
                text=label,
                bootstyle=PRIMARY,
                width=32,
                command=lambda s=spec: app.show_mode(s),
            ).grid(row=row, column=0, pady=6, sticky="ew")
            row += 1


if __name__ == "__main__":
    App().mainloop()
