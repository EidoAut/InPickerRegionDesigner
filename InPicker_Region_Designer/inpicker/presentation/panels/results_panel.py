from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .base import BasePanel


class ResultsPanel(BasePanel):
    """Read-only views of the computed state.

    The summary, table, and payload viewer are treated as separate read models.
    This is a useful UI-level reflection of clean architecture: command actions
    happen elsewhere, while this panel only renders derived state.
    """

    def __init__(self, master, app, *args, **kwargs):
        super().__init__(master, app, *args, **kwargs)
        self._build()

    def _build(self) -> None:
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Results", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            self,
            text="View the current summary, region table and exportable payload.",
            style="Subtitle.TLabel",
            wraplength=560,
        ).grid(row=1, column=0, sticky="w", pady=(4, 12))

        notebook = ttk.Notebook(self)
        notebook.grid(row=2, column=0, sticky="nsew")

        summary_tab = ttk.Frame(notebook, style="Surface.TFrame", padding=10)
        region_tab = ttk.Frame(notebook, style="Surface.TFrame", padding=10)
        payload_tab = ttk.Frame(notebook, style="Surface.TFrame", padding=10)
        notebook.add(summary_tab, text="Summary")
        notebook.add(region_tab, text="Region Data")
        notebook.add(payload_tab, text="Payload")

        summary_tab.rowconfigure(0, weight=1)
        summary_tab.columnconfigure(0, weight=1)
        self.app.summary_text = tk.Text(
            summary_tab,
            wrap="word",
            font=("Consolas", 10),
            bd=0,
            highlightthickness=1,
            highlightbackground=self.palette["border"],
        )
        self.app.summary_text.grid(row=0, column=0, sticky="nsew")

        region_tab.rowconfigure(0, weight=1)
        region_tab.columnconfigure(0, weight=1)
        columns = ("name", "cx", "cy", "cz", "wx", "wy", "wz", "ax", "ay", "az")
        self.app.region_tree = ttk.Treeview(region_tab, columns=columns, show="headings", selectmode="browse")
        headings = {
            "name": "Name",
            "cx": "Cx",
            "cy": "Cy",
            "cz": "Cz",
            "wx": "Wx",
            "wy": "Wy",
            "wz": "Wz",
            "ax": "Ax",
            "ay": "Ay",
            "az": "Az",
        }
        widths = {key: 74 for key in columns}
        widths["name"] = 110
        for key in columns:
            self.app.region_tree.heading(key, text=headings[key])
            self.app.region_tree.column(key, width=widths[key], anchor="center")
        self.app.region_tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll = ttk.Scrollbar(region_tab, orient="vertical", command=self.app.region_tree.yview)
        tree_scroll.grid(row=0, column=1, sticky="ns")
        self.app.region_tree.configure(yscrollcommand=tree_scroll.set)

        payload_tab.rowconfigure(0, weight=1)
        payload_tab.columnconfigure(0, weight=1)
        self.app.payload_text = tk.Text(
            payload_tab,
            wrap="none",
            font=("Consolas", 10),
            bd=0,
            highlightthickness=1,
            highlightbackground=self.palette["border"],
        )
        self.app.payload_text.grid(row=0, column=0, sticky="nsew")

        actions_bar = ttk.Frame(self, style="Surface.TFrame")
        actions_bar.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        ttk.Button(actions_bar, text="Save JSON", command=self.app.save_json, style="Primary.TButton").pack(side="left")
        ttk.Button(actions_bar, text="Load JSON", command=self.app.load_json).pack(side="left", padx=6)
        ttk.Button(actions_bar, text="Evaluate point", command=self.app.eval_point_dialog).pack(side="left", padx=6)
        ttk.Button(actions_bar, text="Copy payload", command=self.app.copy_result_payload).pack(side="left", padx=18)
        ttk.Button(actions_bar, text="Export payload JSON", command=self.app.export_result_payload_json).pack(side="left", padx=6)
        ttk.Button(actions_bar, text="Export regions CSV", command=self.app.export_regions_csv).pack(side="left", padx=6)
