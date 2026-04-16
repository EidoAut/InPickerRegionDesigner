from __future__ import annotations

from tkinter import ttk

from .base import BasePanel


class SimulationPanel(BasePanel):
    """Panel for creating or importing pick samples.

    The simulation configuration is part of the application state because later
    workflows reuse those values. The panel simply edits that state via the host.
    """

    def __init__(self, master, app, *args, **kwargs):
        super().__init__(master, app, *args, **kwargs)
        self._build()

    def _build(self) -> None:
        ttk.Label(self, text="Pick simulation", style="Title.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        ttk.Label(self, text="Number of picks").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(self, textvariable=self.app.sim_n, width=12).grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(self, text="Seed").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(self, textvariable=self.app.sim_seed, width=12).grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Label(self, text="Distribution").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Combobox(
            self,
            textvariable=self.app.sim_mode,
            values=["uniform", "gaussian_center", "bottom_heavy"],
            state="readonly",
            width=18,
        ).grid(row=3, column=1, sticky="ew", pady=4)

        ttk.Button(self, text="Generate picks", command=self.app.generate_simulated_picks, style="Primary.TButton").grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(12, 0)
        )
        ttk.Button(self, text="Import CSV", command=self.app.load_picks_csv).grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )
        ttk.Button(self, text="Clear picks", command=self.app.clear_simulation).grid(
            row=6, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )
        ttk.Label(self, text="CSV format: columns x, y, z", wraplength=330).grid(
            row=7, column=0, columnspan=2, sticky="w", pady=(12, 0)
        )
        self.columnconfigure(1, weight=1)
