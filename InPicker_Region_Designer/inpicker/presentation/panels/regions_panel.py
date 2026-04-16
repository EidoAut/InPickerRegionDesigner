from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .base import BasePanel


class RegionsPanel(BasePanel):
    """Editor for manual region management.

    The panel exposes the list of regions and the editable parameters of the
    currently selected item. It intentionally delegates all mutations back to
    the host window so the mutation flow remains centralized.
    """

    def __init__(self, master, app, *args, **kwargs):
        super().__init__(master, app, *args, **kwargs)
        self._build()

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        ttk.Label(self, text="Regions", style="Title.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))

        # We keep Listbox instead of Treeview here because single selection and
        # keyboard navigation are simple and fast for small region lists.
        self.app.region_listbox = tk.Listbox(
            self,
            height=9,
            exportselection=False,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.palette["border"],
            font=("Segoe UI", 10),
            bg="#ffffff",
            selectbackground="#e5e7eb",
            selectforeground="#1f2937",
        )
        self.app.region_listbox.grid(row=1, column=0, sticky="ew")
        self.app.region_listbox.bind("<<ListboxSelect>>", self.app.on_region_selected)

        editor = ttk.LabelFrame(self, text="Selected region")
        editor.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        for c in range(6):
            editor.columnconfigure(c + 1, weight=1)

        # The host owns the tkinter variables so that refresh operations can
        # update them without needing widget-level knowledge in this panel.
        fields = [
            ("Name", self.app.name_var, 0, 0),
            ("Center X", self.app.cx_var, 1, 0),
            ("Center Y", self.app.cy_var, 1, 2),
            ("Center Z", self.app.cz_var, 1, 4),
            ("Weight X", self.app.wx_var, 2, 0),
            ("Weight Y", self.app.wy_var, 2, 2),
            ("Weight Z", self.app.wz_var, 2, 4),
            ("Approach X", self.app.ax_var, 3, 0),
            ("Approach Y", self.app.ay_var, 3, 2),
            ("Approach Z", self.app.az_var, 3, 4),
            ("Approach Rx", self.app.arx_var, 4, 0),
            ("Approach Ry", self.app.ary_var, 4, 2),
            ("Approach Rz", self.app.arz_var, 4, 4),
        ]
        for label, var, row, col in fields:
            ttk.Label(editor, text=label).grid(row=row, column=col, sticky="w", padx=4, pady=4)
            ttk.Entry(editor, textvariable=var, width=12).grid(row=row, column=col + 1, sticky="ew", padx=(0, 8), pady=4)

        actions = ttk.Frame(self, style="Surface.TFrame")
        actions.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(actions, text="Add", command=self.app.add_region).pack(side="left")
        ttk.Button(actions, text="Save changes", command=self.app.save_region, style="Primary.TButton").pack(side="left", padx=6)
        ttk.Button(actions, text="Duplicate", command=self.app.duplicate_region).pack(side="left", padx=6)
        ttk.Button(actions, text="Delete", command=self.app.delete_region).pack(side="left", padx=6)
