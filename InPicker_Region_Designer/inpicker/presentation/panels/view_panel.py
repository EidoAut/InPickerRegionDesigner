from __future__ import annotations

from tkinter import ttk

from .base import BasePanel


class ViewPanel(BasePanel):
    """Panel for visual outputs.

    Plot generation can be expensive and may depend on optional libraries.
    Keeping the controls isolated here makes the rest of the UI independent from
    those infrastructure-oriented concerns.
    """

    def __init__(self, master, app, *args, **kwargs):
        super().__init__(master, app, *args, **kwargs)
        self._build()

    def _build(self) -> None:
        ttk.Label(self, text="3D view", style="Title.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        ttk.Label(self, text="Isosurface resolution").grid(row=1, column=0, sticky="w")
        ttk.Scale(self, from_=14, to=34, variable=self.app.resolution_var, orient="horizontal").grid(
            row=1, column=1, sticky="ew", padx=(8, 0)
        )
        self.columnconfigure(1, weight=1)

        ttk.Button(self, text="Open surfaces", command=self.app.open_colored_surfaces, style="Accent.TButton").grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(12, 0)
        )
        ttk.Button(self, text="Open regions + picks", command=self.app.open_regions_and_picks, style="Accent.TButton").grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )
        ttk.Label(
            self,
            text="Open a Plotly view of the current regions and optional pick assignments.",
            wraplength=340,
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(12, 0))
