from __future__ import annotations

from tkinter import ttk

from .base import BasePanel


class BinPanel(BasePanel):
    """Panel responsible for bin dimensions and automatic region generation.

    This panel only knows about tkinter controls and host callbacks. It does not
    execute business logic itself. The separation is important because most of
    these actions are application use cases, not presentation concerns.
    """

    def __init__(self, master, app, *args, **kwargs):
        super().__init__(master, app, *args, **kwargs)
        self._build()

    def _build(self) -> None:
        # The panel is intentionally form-like: it groups the parameters in the
        # same order the user typically works with them.
        ttk.Label(self, text="Bin", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10)
        )

        for row_idx, (label, var) in enumerate(
            [("X", self.app.bin_x), ("Y", self.app.bin_y), ("Z", self.app.bin_z)], start=1
        ):
            ttk.Label(self, text=f"{label} dimension").grid(row=row_idx, column=0, sticky="w", pady=5)
            ttk.Entry(self, textvariable=var, width=14).grid(row=row_idx, column=1, sticky="ew", pady=5)

        ttk.Button(self, text="Apply dimensions", command=self.app.apply_bin_dims).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(12, 0)
        )
        ttk.Button(self, text="Auto-generate 4 regions", command=self.app.auto_generate_four).grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )
        ttk.Button(self, text="Auto-generate 8 regions", command=self.app.auto_generate_eight).grid(
            row=6, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )

        ttk.Separator(self, orient="horizontal").grid(row=7, column=0, columnspan=2, sticky="ew", pady=(14, 10))
        ttk.Label(self, text="Auto-generation", style="Title.TLabel").grid(
            row=8, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )

        ttk.Label(self, text="Region count").grid(row=9, column=0, sticky="w", pady=4)
        ttk.Spinbox(self, from_=2, to=16, textvariable=self.app.auto_region_count, width=10).grid(
            row=9, column=1, sticky="w", pady=4
        )

        ttk.Label(self, text="Seed strategy").grid(row=10, column=0, sticky="w", pady=4)
        ttk.Combobox(
            self,
            textvariable=self.app.auto_init_mode,
            values=["from_picks", "grid"],
            state="readonly",
            width=16,
        ).grid(row=10, column=1, sticky="ew", pady=4)

        ttk.Label(self, text="Generation mode").grid(row=11, column=0, sticky="w", pady=4)
        ttk.Combobox(
            self,
            textvariable=self.app.auto_generation_mode,
            values=["smart", "layers"],
            state="readonly",
            width=16,
        ).grid(row=11, column=1, sticky="ew", pady=4)

        ttk.Label(self, text="Layer count").grid(row=12, column=0, sticky="w", pady=4)
        ttk.Spinbox(self, from_=1, to=8, textvariable=self.app.layer_count_var, width=10).grid(
            row=12, column=1, sticky="w", pady=4
        )

        ttk.Label(self, text="Balance strength").grid(row=13, column=0, sticky="w", pady=4)
        ttk.Scale(self, from_=0.0, to=1.0, variable=self.app.auto_balance_strength, orient="horizontal").grid(
            row=13, column=1, sticky="ew", pady=4
        )

        ttk.Label(self, text="Target load %").grid(row=14, column=0, sticky="w", pady=4)
        ttk.Entry(self, textvariable=self.app.auto_target_loads, width=18).grid(
            row=14, column=1, sticky="ew", pady=4
        )

        ttk.Button(self, text="Generate regions", command=self.app.auto_generate_from_data, style="Primary.TButton").grid(
            row=15, column=0, columnspan=2, sticky="ew", pady=(10, 0)
        )
        ttk.Button(self, text="Generate by layers", command=self.app.auto_generate_by_layers).grid(
            row=16, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )
        ttk.Button(self, text="Optimize load balance", command=self.app.optimize_region_loads).grid(
            row=17, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )

        detect_frame = ttk.Frame(self, style="Surface.TFrame")
        detect_frame.grid(row=18, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Label(detect_frame, text="Detect ideal K").pack(side="left")
        ttk.Spinbox(detect_frame, from_=2, to=20, textvariable=self.app.auto_k_min, width=5).pack(side="left", padx=(8, 4))
        ttk.Label(detect_frame, text="to").pack(side="left")
        ttk.Spinbox(detect_frame, from_=2, to=20, textvariable=self.app.auto_k_max, width=5).pack(side="left", padx=4)
        ttk.Button(self, text="Detect ideal count", command=self.app.detect_ideal_region_count).grid(
            row=19, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )

        ttk.Label(
            self,
            text="Target load % accepts comma-separated values like 40,30,20,10. Leave empty for automatic balancing.",
            wraplength=340,
        ).grid(row=20, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self.columnconfigure(1, weight=1)
