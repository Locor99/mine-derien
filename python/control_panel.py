import sys
import tkinter as tk
from tkinter import ttk

from serial_link import SerialLink, find_arduino_port

SECTION_COUNT = 37
GRID_COLUMNS = 8
POLL_INTERVAL_MS = 200

DEFAULT_FREQUENCY_HZ = "15"
DEFAULT_DUTY_PERCENT = "25"

PRESENT_COLOR = "#3aaa3a"
ABSENT_COLOR = "#cccccc"
UNKNOWN_COLOR = "#e8e8e8"


def decode_state(hex_string):
    present = [False] * SECTION_COUNT
    for nibble_index, hex_char in enumerate(hex_string):
        try:
            value = int(hex_char, 16)
        except ValueError:
            return present
        for bit in range(4):
            section = nibble_index * 4 + bit
            if section < SECTION_COUNT:
                present[section] = bool(value & (1 << bit))
    return present


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


class SectionLight:
    def __init__(self, parent, section):
        self.frame = ttk.Frame(parent)
        ttk.Label(self.frame, text=str(section), width=3).pack()
        self.light = tk.Label(self.frame, width=6, height=2, bg=UNKNOWN_COLOR)
        self.light.pack()

    def show_presence(self, present):
        self.light.configure(bg=PRESENT_COLOR if present else ABSENT_COLOR)


class ControlPanel:
    def __init__(self, root, port):
        self.root = root
        self.link = None
        self.sections = []
        self.auto_lights = []
        self.auto_running = False
        root.title("Mine Derien — Panneau de commande")

        self.status = tk.StringVar(value="Non connecté")
        self.port = tk.StringVar(value=port or "")
        self.raw_pin = tk.StringVar()
        self.raw_value = tk.StringVar(value="1")
        self.raw_result = tk.StringVar(value="")
        self.auto_frequency = tk.StringVar(value=DEFAULT_FREQUENCY_HZ)
        self.auto_duty = tk.StringVar(value=DEFAULT_DUTY_PERCENT)
        self.auto_status = tk.StringVar(value="ARRÊT")

        self._build_connection_bar(root)

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)
        test_tab = ttk.Frame(notebook)
        auto_tab = ttk.Frame(notebook)
        notebook.add(test_tab, text="Test")
        notebook.add(auto_tab, text="Auto")
        self._build_test_tab(test_tab)
        self._build_auto_tab(auto_tab)

        if port:
            self.connect()
        self.root.after(POLL_INTERVAL_MS, self.poll_auto_state)

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

    def _build_auto_tab(self, tab):
        controls = ttk.Frame(tab)
        controls.pack(fill="x", padx=8, pady=8)
        ttk.Label(controls, text="Fréquence (Hz) :").pack(side="left", padx=(0, 2))
        ttk.Entry(controls, textvariable=self.auto_frequency, width=6).pack(side="left")
        ttk.Label(controls, text="Duty (%) :").pack(side="left", padx=(8, 2))
        ttk.Entry(controls, textvariable=self.auto_duty, width=6).pack(side="left")
        ttk.Button(controls, text="Démarrer",
                   command=self.handle_auto_start).pack(side="left", padx=(12, 2))
        ttk.Button(controls, text="Arrêter",
                   command=self.handle_auto_stop).pack(side="left")
        ttk.Label(controls, textvariable=self.auto_status).pack(side="left", padx=12)

        grid = ttk.Frame(tab)
        grid.pack(padx=8, pady=8)
        for section in range(SECTION_COUNT):
            light = SectionLight(grid, section)
            light.frame.grid(row=section // GRID_COLUMNS,
                             column=section % GRID_COLUMNS,
                             padx=3, pady=3)
            self.auto_lights.append(light)

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

    def handle_auto_start(self):
        frequency = self.auto_frequency.get().strip()
        duty = self.auto_duty.get().strip()
        reply = self.request(f"AUTO_START {frequency} {duty}")
        if reply == "OK":
            self.auto_running = True
            self.auto_status.set(f"ROULE — F={frequency} Hz, D={duty} %")
        elif reply is not None:
            self.auto_status.set("Paramètres refusés")

    def handle_auto_stop(self):
        reply = self.request("AUTO_STOP")
        if reply is not None:
            self.auto_running = False
            self.auto_status.set("ARRÊT")

    def poll_auto_state(self):
        if self.auto_running and self.link is not None:
            reply = self.link.request("GET_STATE")
            if reply is not None and len(reply) == 10:
                for section, present in enumerate(decode_state(reply)):
                    self.auto_lights[section].show_presence(present)
        self.root.after(POLL_INTERVAL_MS, self.poll_auto_state)


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else find_arduino_port()
    root = tk.Tk()
    ControlPanel(root, port)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
