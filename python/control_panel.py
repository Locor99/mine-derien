import sys
import tkinter as tk
from tkinter import ttk

from serial_link import SerialLink, find_arduino_port

SECTION_COUNT = 37
GRID_COLUMNS = 8

PRESENT_COLOR = "#3aaa3a"
ABSENT_COLOR = "#cccccc"
UNKNOWN_COLOR = "#e8e8e8"


class SectionWidget:
    def __init__(self, parent, section, on_scan, on_energize):
        self.frame = ttk.LabelFrame(parent, text=f"Section {section}")
        self.indicator = tk.Label(self.frame, text="?", width=8, bg=UNKNOWN_COLOR)
        self.indicator.grid(row=0, column=0, columnspan=2, pady=2, padx=2)
        ttk.Button(self.frame, text="Scan", width=6,
                   command=lambda: on_scan(section)).grid(row=1, column=0, padx=1, pady=1)
        ttk.Button(self.frame, text="Énergiser", width=9,
                   command=lambda: on_energize(section)).grid(row=1, column=1, padx=1, pady=1)

    def show_presence(self, present):
        self.indicator.configure(
            bg=PRESENT_COLOR if present else ABSENT_COLOR,
            text="Train" if present else "Vide")


class ControlPanel:
    def __init__(self, root, port):
        self.root = root
        self.link = None
        self.sections = []
        root.title("Mine Derien — Panneau de commande")

        self.status = tk.StringVar(value="Non connecté")
        self.port = tk.StringVar(value=port or "")
        self.raw_pin = tk.StringVar()
        self.raw_value = tk.StringVar(value="1")
        self.raw_result = tk.StringVar(value="")

        self._build_connection_bar(root)

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)
        test_tab = ttk.Frame(notebook)
        notebook.add(test_tab, text="Test")
        self._build_test_tab(test_tab)

        if port:
            self.connect()

    def _build_connection_bar(self, parent):
        bar = ttk.Frame(parent)
        bar.pack(fill="x", padx=8, pady=(8, 0))
        ttk.Label(bar, text="Port :").pack(side="left")
        ttk.Entry(bar, textvariable=self.port, width=18).pack(side="left", padx=4)
        ttk.Button(bar, text="Connecter", command=self.connect).pack(side="left")
        ttk.Label(bar, textvariable=self.status).pack(side="left", padx=12)

    def _build_test_tab(self, tab):
        grid = ttk.Frame(tab)
        grid.pack(padx=8, pady=8)
        for section in range(SECTION_COUNT):
            widget = SectionWidget(grid, section, self.handle_scan, self.handle_energize)
            widget.frame.grid(row=section // GRID_COLUMNS,
                              column=section % GRID_COLUMNS,
                              padx=3, pady=3, sticky="nsew")
            self.sections.append(widget)

        actions = ttk.Frame(tab)
        actions.pack(fill="x", padx=8, pady=8)
        ttk.Button(actions, text="Tout désénergiser",
                   command=self.handle_deenergize_all).pack(side="left")

        raw = ttk.LabelFrame(tab, text="Pin brute")
        raw.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Label(raw, text="Pin :").pack(side="left", padx=(6, 2))
        ttk.Entry(raw, textvariable=self.raw_pin, width=6).pack(side="left")
        ttk.Label(raw, text="Valeur :").pack(side="left", padx=(8, 2))
        ttk.Entry(raw, textvariable=self.raw_value, width=4).pack(side="left")
        ttk.Button(raw, text="SET", command=self.handle_raw_set).pack(side="left", padx=4)
        ttk.Button(raw, text="GET", command=self.handle_raw_get).pack(side="left")
        ttk.Label(raw, textvariable=self.raw_result).pack(side="left", padx=12)

    def connect(self):
        port = self.port.get().strip()
        if not port:
            self.status.set("Aucun port indiqué")
            return
        if self.link is not None:
            self.link.close()
            self.link = None
        try:
            link = SerialLink(port)
        except Exception as error:
            self.status.set(f"Échec connexion : {error}")
            return
        self.link = link
        if link.request("PING") == "PONG":
            self.status.set(f"Connecté — {port}")
        else:
            self.status.set(f"Connecté — {port} (pas de PONG)")

    def request(self, command):
        if self.link is None:
            self.status.set("Non connecté")
            return None
        return self.link.request(command)

    def handle_scan(self, section):
        reply = self.request(f"SCAN {section}")
        if reply is not None:
            self.sections[section].show_presence(reply == "1")

    def handle_energize(self, section):
        self.request(f"ENERGIZE {section}")

    def handle_deenergize_all(self):
        self.request("DEENERGIZE_ALL")

    def handle_raw_get(self):
        reply = self.request(f"GET {self.raw_pin.get().strip()}")
        if reply is not None:
            self.raw_result.set(f"→ {reply}")

    def handle_raw_set(self):
        pin = self.raw_pin.get().strip()
        value = self.raw_value.get().strip()
        reply = self.request(f"SET {pin} {value}")
        if reply is not None:
            self.raw_result.set(f"→ {reply}")


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else find_arduino_port()
    root = tk.Tk()
    ControlPanel(root, port)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
