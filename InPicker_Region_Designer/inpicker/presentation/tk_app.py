from __future__ import annotations

import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from inpicker.application.bootstrap import build_controller
from inpicker.infrastructure.plotly_visualizer import PLOTLY_OK, SKIMAGE_OK
from inpicker.presentation.panels.bin_panel import BinPanel
from inpicker.presentation.panels.regions_panel import RegionsPanel
from inpicker.presentation.panels.results_panel import ResultsPanel
from inpicker.presentation.panels.simulation_panel import SimulationPanel
from inpicker.presentation.panels.view_panel import ViewPanel


class App(tk.Tk):
    """Tkinter composition root for the desktop application.

    Architecture notes:
    - The controller is the presentation-facing application boundary.
    - This class coordinates shared tkinter state and cross-panel refresh logic.
    - Individual tabs and read-only sections live in dedicated panel modules.

    The goal is not to eliminate a central window class entirely, but to keep it
    focused on orchestration instead of widget construction and domain logic.
    """

    def __init__(self):
        super().__init__()
        self.title("InPicker Region Designer")
        self.geometry("1420x880")
        self.minsize(1280, 820)
        self.configure(bg="#f5f7fa")

        self.palette = {
            "bg": "#f5f7fa",
            "surface": "#ffffff",
            "surface_alt": "#f8fafc",
            "ink": "#111827",
            "muted": "#6b7280",
            "accent": "#111827",
            "accent_soft": "#eef2f7",
            "border": "#e5e7eb",
            "success": "#0f766e",
        }

        self.controller = build_controller()

        # ------------------------------------------------------------------
        # Tk variables: these are presentation state, not domain state.
        # They intentionally sit in the host app because several panels and
        # refresh routines must access them.
        # ------------------------------------------------------------------
        self._init_variables()
        self._init_widget_references()

        self._build_style()
        self._build_shell()
        self.controller.bootstrap()
        self.refresh_from_state()

    def _init_variables(self) -> None:
        """Create all tkinter variables in one place.

        Grouping them here makes it easier to see which values are edited in the
        UI and later synchronized into the application state.
        """

        self.bin_x = tk.DoubleVar(value=600.0)
        self.bin_y = tk.DoubleVar(value=400.0)
        self.bin_z = tk.DoubleVar(value=300.0)

        self.auto_region_count = tk.IntVar(value=4)
        self.auto_init_mode = tk.StringVar(value="from_picks")
        self.auto_generation_mode = tk.StringVar(value="smart")
        self.auto_balance_strength = tk.DoubleVar(value=0.35)
        self.auto_target_loads = tk.StringVar(value="")
        self.layer_count_var = tk.IntVar(value=2)
        self.auto_k_min = tk.IntVar(value=2)
        self.auto_k_max = tk.IntVar(value=10)

        self.name_var = tk.StringVar()
        self.cx_var = tk.DoubleVar()
        self.cy_var = tk.DoubleVar()
        self.cz_var = tk.DoubleVar()
        self.wx_var = tk.DoubleVar(value=1.0)
        self.wy_var = tk.DoubleVar(value=1.0)
        self.wz_var = tk.DoubleVar(value=1.2)
        self.ax_var = tk.DoubleVar()
        self.ay_var = tk.DoubleVar()
        self.az_var = tk.DoubleVar()
        self.arx_var = tk.DoubleVar(value=0.0)
        self.ary_var = tk.DoubleVar(value=0.0)
        self.arz_var = tk.DoubleVar(value=0.0)

        self.sim_n = tk.IntVar(value=250)
        self.sim_seed = tk.IntVar(value=42)
        self.sim_mode = tk.StringVar(value="uniform")
        self.resolution_var = tk.IntVar(value=20)

    def _init_widget_references(self) -> None:
        """Initialize widget references filled later by panel objects.

        Using explicit attributes here keeps type expectations clear and avoids
        accidental creation of ad-hoc attributes across methods.
        """

        self.metric_regions = None
        self.metric_picks = None
        self.metric_mode = None
        self.region_listbox = None
        self.summary_text = None
        self.region_tree = None
        self.payload_text = None
        self.selected_index = None

    def _build_style(self) -> None:
        """Configure ttk styles shared across the whole UI."""
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            # Falling back to the default theme is acceptable; styling is a nice
            # to have, not a startup requirement.
            pass

        p = self.palette
        self.option_add("*Font", "{Segoe UI} 10")
        self.option_add("*TCombobox*Listbox.font", "{Segoe UI} 10")

        style.configure("App.TFrame", background=p["bg"])
        style.configure("Surface.TFrame", background=p["surface"])
        style.configure("SurfaceAlt.TFrame", background=p["surface_alt"])
        style.configure("Card.TFrame", background=p["surface"], relief="solid", borderwidth=1)
        style.configure("Hero.TFrame", background=p["surface"])
        style.configure("Sidebar.TFrame", background=p["surface"])

        style.configure("Title.TLabel", background=p["surface"], foreground=p["ink"], font=("Segoe UI", 15, "bold"))
        style.configure("Section.TLabel", background=p["surface"], foreground=p["ink"], font=("Segoe UI", 11, "bold"))
        style.configure("HeroTitle.TLabel", background=p["surface"], foreground=p["ink"], font=("Segoe UI", 18, "bold"))
        style.configure("Subtitle.TLabel", background=p["surface"], foreground=p["muted"], font=("Segoe UI", 9))
        style.configure("MetricValue.TLabel", background=p["surface_alt"], foreground=p["ink"], font=("Segoe UI", 16, "bold"))
        style.configure("MetricLabel.TLabel", background=p["surface_alt"], foreground=p["muted"], font=("Segoe UI", 8))
        style.configure("TLabel", background=p["surface"], foreground=p["ink"])
        style.configure("TLabelframe", background=p["surface"], borderwidth=1)
        style.configure("TLabelframe.Label", background=p["surface"], foreground=p["ink"], font=("Segoe UI", 10, "bold"))

        style.configure("TNotebook", background=p["surface"], borderwidth=0, tabmargins=(2, 4, 2, 0))
        style.configure("TNotebook.Tab", background="#f1f5f9", foreground=p["ink"], padding=(14, 8), font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", p["surface"]), ("active", p["accent_soft"])] , foreground=[("selected", p["ink"]), ("active", p["ink"])])

        style.configure("TButton", padding=(10, 7), background="#f3f4f6", foreground=p["ink"], bordercolor=p["border"], focusthickness=0)
        style.map("TButton", background=[("active", p["accent_soft"]), ("pressed", "#e5e7eb")])
        style.configure("Primary.TButton", background=p["accent"], foreground="#ffffff", font=("Segoe UI", 10, "bold"))
        style.map("Primary.TButton", background=[("active", "#1f2937"), ("pressed", "#000000")], foreground=[("active", "#ffffff")])
        style.configure("Accent.TButton", background="#374151", foreground="#ffffff", font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#1f2937"), ("pressed", "#111827")], foreground=[("active", "#ffffff")])

        style.configure("Treeview", rowheight=26, font=("Segoe UI", 10), borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def _build_shell(self) -> None:
        """Build the top-level layout and attach the panel objects."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        shell = ttk.Panedwindow(self, orient="horizontal")
        shell.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)

        left = ttk.Frame(shell, style="Sidebar.TFrame", padding=14)
        right = ttk.Frame(shell, style="Surface.TFrame", padding=14)
        shell.add(left, weight=3)
        shell.add(right, weight=4)

        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        self._build_left_tabs(left)
        self.results_panel = ResultsPanel(right, self, style="Surface.TFrame")
        self.results_panel.grid(row=0, column=0, sticky="nsew")

    def _build_metrics(self, parent) -> None:
        """Top summary cards.

        The labels are stored on the host because they are updated from the same
        refresh path that also updates the text views and tables.
        """
        metrics = ttk.Frame(parent, style="Surface.TFrame")
        metrics.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        for i in range(3):
            metrics.columnconfigure(i, weight=1)

        self.metric_regions = ttk.Label(metrics, text="0", style="MetricValue.TLabel", anchor="center")
        self.metric_picks = ttk.Label(metrics, text="0", style="MetricValue.TLabel", anchor="center")
        self.metric_mode = ttk.Label(metrics, text="smart", style="MetricValue.TLabel", anchor="center")
        specs = [
            ("Regions", self.metric_regions),
            ("Picks", self.metric_picks),
            ("Mode", self.metric_mode),
        ]
        for col, (label_text, widget) in enumerate(specs):
            card = ttk.Frame(metrics, style="SurfaceAlt.TFrame", padding=10)
            card.grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 6, 0))
            card.columnconfigure(0, weight=1)
            widget.grid(in_=card, row=0, column=0, sticky="ew")
            ttk.Label(card, text=label_text, style="MetricLabel.TLabel", anchor="center").grid(
                row=1, column=0, sticky="ew", pady=(4, 0)
            )

    def _build_left_tabs(self, parent) -> None:
        notebook_holder = ttk.Frame(parent, style="Surface.TFrame")
        notebook_holder.grid(row=0, column=0, sticky="nsew")
        notebook_holder.rowconfigure(0, weight=1)
        notebook_holder.columnconfigure(0, weight=1)

        notebook = ttk.Notebook(notebook_holder)
        notebook.grid(row=0, column=0, sticky="nsew")

        self.bin_panel = BinPanel(notebook, self, style="Surface.TFrame", padding=14)
        self.regions_panel = RegionsPanel(notebook, self, style="Surface.TFrame", padding=14)
        self.simulation_panel = SimulationPanel(notebook, self, style="Surface.TFrame", padding=14)
        self.view_panel = ViewPanel(notebook, self, style="Surface.TFrame", padding=14)

        notebook.add(self.bin_panel, text="1. Bin")
        notebook.add(self.regions_panel, text="2. Regions")
        notebook.add(self.simulation_panel, text="3. Simulation")
        notebook.add(self.view_panel, text="4. 3D View")

    # ------------------------------------------------------------------
    # Synchronization helpers
    # ------------------------------------------------------------------
    def _sync_auto_generation_config_to_state(self) -> None:
        """Push UI controls into the application state.

        This fixes an important correctness issue from the earlier version: the
        user could edit the controls visually, but some use cases still consumed
        stale values from the state object.
        """
        auto = self.controller.state.auto_generation
        auto.region_count = int(self.auto_region_count.get())
        auto.init_mode = self.auto_init_mode.get().strip() or "from_picks"
        auto.generation_mode = self.auto_generation_mode.get().strip() or "smart"
        auto.balance_strength = float(self.auto_balance_strength.get())
        auto.target_loads_raw = self.auto_target_loads.get()
        auto.layer_count = int(self.layer_count_var.get())
        auto.ideal_k_min = int(self.auto_k_min.get())
        auto.ideal_k_max = int(self.auto_k_max.get())

    def _sync_simulation_config_to_state(self) -> None:
        simulation = self.controller.state.simulation
        simulation.count = int(self.sim_n.get())
        simulation.seed = int(self.sim_seed.get())
        simulation.mode = self.sim_mode.get().strip() or "uniform"

    # ------------------------------------------------------------------
    # Actions wired from panels
    # ------------------------------------------------------------------
    def apply_bin_dims(self) -> None:
        try:
            self.controller.apply_bin_dimensions(float(self.bin_x.get()), float(self.bin_y.get()), float(self.bin_z.get()))
            self.refresh_from_state()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid bin dimensions.\n{e}")

    def auto_generate_four(self) -> None:
        self.controller.auto_generate_default(4)
        self.refresh_from_state()

    def auto_generate_eight(self) -> None:
        self.controller.auto_generate_default(8)
        self.refresh_from_state()

    def auto_generate_from_data(self) -> None:
        try:
            self._sync_auto_generation_config_to_state()
            source = self.controller.auto_generate_from_data()
            self.refresh_from_state()
            suffix = " with target load profile" if self.auto_target_loads.get().strip() else ""
            messagebox.showinfo(
                "Auto-generation",
                f"Generated {len(self.controller.state.regions)} regions automatically from {source}{suffix}.\n\n"
                "The exported payload now includes the defined region data.",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to auto-generate regions.\n{e}")

    def auto_generate_by_layers(self) -> None:
        try:
            self._sync_auto_generation_config_to_state()
            result = self.controller.auto_generate_by_layers()
            self.refresh_from_state()
            messagebox.showinfo(
                "Layer generation",
                f"Generated {len(self.controller.state.regions)} regions in {int(self.layer_count_var.get())} layers from {result['source_points']}.\n\n"
                "Region data is available in Region Data and Payload.",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to auto-generate layered regions.\n{e}")

    def optimize_region_loads(self) -> None:
        try:
            self._sync_auto_generation_config_to_state()
            result = self.controller.optimize_region_loads()
            self.refresh_from_state()
            pct = ", ".join(f"{100*v:.1f}%" for v in result["target_loads_normalized"])
            messagebox.showinfo(
                "Load optimization",
                f"Optimized {len(self.controller.state.regions)} regions from {result['source_points']}. Target profile: {pct}\n\n"
                "The result payload includes all defined regions.",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to optimize region loads.\n{e}")

    def detect_ideal_region_count(self) -> None:
        try:
            self._sync_auto_generation_config_to_state()
            result = self.controller.detect_ideal_region_count()
            self.refresh_from_state()
            self.summary_text.delete("1.0", "end")
            self.summary_text.insert("1.0", "\n".join(result["summary_lines"] + ["", f"Selected ideal region count: {result['selected_k']}"]))
            messagebox.showinfo(
                "Ideal region count",
                f"Detected K={result['selected_k']} as the best region count in the scanned range.\n\n"
                "The selected regions are available for export.",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to detect the ideal region count.\n{e}")

    def add_region(self) -> None:
        self.controller.add_region()
        self.refresh_from_state()

    def duplicate_region(self) -> None:
        self.controller.state.selected_index = self.selected_index
        self.controller.duplicate_region()
        self.refresh_from_state()

    def delete_region(self) -> None:
        self.controller.state.selected_index = self.selected_index
        self.controller.delete_region()
        self.refresh_from_state()

    def on_region_selected(self, _event=None) -> None:
        selection = self.region_listbox.curselection()
        if not selection:
            return
        self.selected_index = selection[0]
        self.controller.state.selected_index = self.selected_index
        self.load_region_editor()

    def load_region_editor(self) -> None:
        if self.selected_index is None or self.selected_index >= len(self.controller.state.regions):
            return
        region = self.controller.state.regions[self.selected_index].to_dict()
        self.name_var.set(region["name"])
        self.cx_var.set(region["center"]["x"])
        self.cy_var.set(region["center"]["y"])
        self.cz_var.set(region["center"]["z"])
        self.wx_var.set(region["weights"]["x"])
        self.wy_var.set(region["weights"]["y"])
        self.wz_var.set(region["weights"]["z"])
        self.ax_var.set(region["approach"]["x"])
        self.ay_var.set(region["approach"]["y"])
        self.az_var.set(region["approach"]["z"])
        self.arx_var.set(region["approach"]["rx"])
        self.ary_var.set(region["approach"]["ry"])
        self.arz_var.set(region["approach"]["rz"])

    def save_region(self) -> None:
        if self.selected_index is None:
            return
        try:
            payload = {
                "name": self.name_var.get(),
                "center": {"x": float(self.cx_var.get()), "y": float(self.cy_var.get()), "z": float(self.cz_var.get())},
                "weights": {"x": float(self.wx_var.get()), "y": float(self.wy_var.get()), "z": float(self.wz_var.get())},
                "approach": {
                    "x": float(self.ax_var.get()),
                    "y": float(self.ay_var.get()),
                    "z": float(self.az_var.get()),
                    "rx": float(self.arx_var.get()),
                    "ry": float(self.ary_var.get()),
                    "rz": float(self.arz_var.get()),
                },
            }
            self.controller.save_region(self.selected_index, payload)
            self.refresh_from_state()
        except Exception:
            messagebox.showerror("Error", "Invalid region parameters.")

    def generate_simulated_picks(self) -> None:
        try:
            self._sync_simulation_config_to_state()
            count = self.controller.generate_simulated_picks()
            self.refresh_from_state()
            messagebox.showinfo("Simulation", f"Generated {count} simulated picks.")
        except Exception:
            messagebox.showerror("Error", "Failed to generate simulated picks.")

    def load_picks_csv(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        try:
            count = self.controller.load_picks_csv(path)
            self.refresh_from_state()
            messagebox.showinfo("CSV", f"Loaded {count} picks.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV.\n{e}")

    def clear_simulation(self) -> None:
        self.controller.clear_simulation()
        self.refresh_from_state()

    def open_regions_and_picks(self) -> None:
        try:
            self.controller.open_regions_and_picks()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_colored_surfaces(self) -> None:
        try:
            self.controller.open_colored_surfaces(int(self.resolution_var.get()))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_json(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        self.controller.save_json(path)
        messagebox.showinfo("Saved", "Configuration saved successfully, including the latest result payload.")

    def load_json(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path:
            return
        self.controller.load_json(path)
        self.refresh_from_state()

    def copy_result_payload(self) -> None:
        payload = json.dumps(self.controller.state.last_result_payload, indent=2, ensure_ascii=False)
        self.clipboard_clear()
        self.clipboard_append(payload)
        self.update_idletasks()
        messagebox.showinfo("Copied", "Latest result payload copied to clipboard.")

    def export_result_payload_json(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        self.controller.export_payload(path)
        messagebox.showinfo("Exported", "Latest result payload exported successfully.")

    def export_regions_csv(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        rows = self.controller.region_rows()
        if not rows:
            messagebox.showwarning("No data", "There are no regions to export.")
            return
        self.controller.export_regions_csv(path)
        messagebox.showinfo("Exported", "Region data exported successfully to CSV.")

    def _format_point_evaluation_details(self, result_payload: dict) -> str:
        point = result_payload.get("point", {})
        point_text = (
            f"Evaluated point: ({point.get('x', 0.0):.3f}, "
            f"{point.get('y', 0.0):.3f}, {point.get('z', 0.0):.3f})"
        )
        if result_payload.get("selected_region_index") is None:
            return "\n".join([
                point_text,
                result_payload.get("message", "No regions are defined."),
            ])

        status_text = "inside" if result_payload.get("inside_bin") else "outside"
        assigned_region = result_payload.get("selected_region_name", "-")
        lines = [
            point_text,
            f"Status: the point is {status_text} the bin.",
            f"Assigned region: {assigned_region} (index {result_payload['selected_region_index']}).",
            f"Winning cost: {result_payload['winning_cost']:.6f}",
        ]
        if result_payload.get("inside_bin"):
            lines.append(f"Conclusion: the point is inside the bin and belongs to region {assigned_region}.")
        else:
            lines.append(
                f"Conclusion: the point is outside the bin. By mathematical proximity, it would still be associated with region {assigned_region}."
            )
        if result_payload.get("runner_up_region_name") is not None:
            lines.extend([
                "",
                "Closest comparison:",
                f"  • Runner-up region: {result_payload['runner_up_region_name']}",
                f"  • Runner-up cost: {result_payload['runner_up_cost']:.6f}",
                f"  • Decision margin: {result_payload['decision_margin']:.6f}",
            ])
        lines.extend(["", "Region costs:"])
        for item in result_payload.get("costs", []):
            lines.append(f"  - {item['region']} (index {item['region_index']}): {item['cost']:.6f}")
        lines.extend(["", "Technical payload:", json.dumps(result_payload, indent=2, ensure_ascii=False)])
        return "\n".join(lines)

    def eval_point_dialog(self) -> None:
        """Open a small dialog that evaluates a 3D point against current regions."""
        win = tk.Toplevel(self)
        win.title("Evaluate point")
        win.configure(bg=self.palette["bg"])
        win.columnconfigure(1, weight=1)
        win.columnconfigure(2, weight=1)
        win.rowconfigure(4, weight=1)

        vars_ = {
            "x": tk.DoubleVar(value=self.controller.state.bin_dimensions.x / 2),
            "y": tk.DoubleVar(value=self.controller.state.bin_dimensions.y / 2),
            "z": tk.DoubleVar(value=self.controller.state.bin_dimensions.z / 2),
        }
        for i, axis in enumerate(("x", "y", "z")):
            ttk.Label(win, text=axis.upper()).grid(row=i, column=0, padx=8, pady=6, sticky="w")
            ttk.Entry(win, textvariable=vars_[axis], width=16).grid(row=i, column=1, padx=8, pady=6, sticky="ew")

        summary = tk.Frame(
            win,
            bg=self.palette["surface_alt"],
            highlightthickness=1,
            highlightbackground=self.palette["border"],
        )
        summary.grid(row=0, column=2, rowspan=4, padx=(8, 10), pady=8, sticky="nsew")
        summary.columnconfigure(0, weight=1)
        tk.Label(
            summary,
            text="Point evaluation",
            font=("Segoe UI", 12, "bold"),
            bg=self.palette["surface_alt"],
            fg=self.palette["ink"],
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 4))
        status_var = tk.StringVar(value="Pending")
        bin_var = tk.StringVar(value="-")
        region_var = tk.StringVar(value="-")
        conclusion_var = tk.StringVar(value="Enter a point to evaluate it.")
        summary_rows = (("Status", status_var), ("Inside bin", bin_var), ("Region", region_var))
        row_idx = 1
        for label, var in summary_rows:
            tk.Label(
                summary,
                text=label,
                font=("Segoe UI", 9, "bold"),
                bg=self.palette["surface_alt"],
                fg=self.palette["muted"],
            ).grid(row=row_idx, column=0, sticky="w", padx=10)
            row_idx += 1
            tk.Label(
                summary,
                textvariable=var,
                font=("Segoe UI", 11),
                bg=self.palette["surface_alt"],
                fg=self.palette["ink"],
                wraplength=280,
                justify="left",
            ).grid(row=row_idx, column=0, sticky="w", padx=10, pady=(0, 6))
            row_idx += 1
        tk.Label(
            summary,
            text="Conclusion",
            font=("Segoe UI", 9, "bold"),
            bg=self.palette["surface_alt"],
            fg=self.palette["muted"],
        ).grid(row=row_idx, column=0, sticky="w", padx=10)
        row_idx += 1
        tk.Label(
            summary,
            textvariable=conclusion_var,
            font=("Segoe UI", 11),
            bg=self.palette["surface_alt"],
            fg=self.palette["ink"],
            wraplength=280,
            justify="left",
        ).grid(row=row_idx, column=0, sticky="w", padx=10, pady=(0, 10))

        output = tk.Text(
            win,
            width=90,
            height=18,
            font=("Consolas", 10),
            bd=0,
            highlightthickness=1,
            highlightbackground=self.palette["border"],
        )
        output.grid(row=4, column=0, columnspan=3, padx=8, pady=8, sticky="nsew")

        def run() -> None:
            try:
                point = (float(vars_["x"].get()), float(vars_["y"].get()), float(vars_["z"].get()))
                result_payload = self.controller.evaluate_point(point)
            except Exception as e:
                status_var.set("Error")
                bin_var.set("-")
                region_var.set("-")
                conclusion_var.set(str(e))
                output.delete("1.0", "end")
                output.insert("1.0", f"Error evaluating point:\n{e}")
                return
            output.delete("1.0", "end")
            if result_payload.get("selected_region_index") is None:
                status_var.set("No regions")
                bin_var.set("Yes" if result_payload.get("inside_bin") else "No")
                region_var.set("Not available")
                conclusion_var.set(result_payload.get("message", "No regions are defined."))
                output.insert("1.0", self._format_point_evaluation_details(result_payload))
                self.refresh_payload_view()
                return

            inside_bin = bool(result_payload.get("inside_bin"))
            assigned_region = result_payload.get("selected_region_name", "-")
            status_var.set("Inside bin" if inside_bin else "Outside bin")
            bin_var.set("Yes" if inside_bin else "No")
            region_var.set(assigned_region)
            if inside_bin:
                conclusion_var.set(f"The point is inside the bin and belongs to region {assigned_region}.")
            else:
                conclusion_var.set(f"The point is outside the bin; the closest region is {assigned_region}.")
            output.insert("1.0", self._format_point_evaluation_details(result_payload))
            self.refresh_payload_view()

        ttk.Button(win, text="Evaluate", command=run, style="Primary.TButton").grid(row=3, column=0, columnspan=2, pady=(4, 0))
        run()

    # ------------------------------------------------------------------
    # Read-model refresh methods
    # ------------------------------------------------------------------
    def refresh_region_list(self) -> None:
        self.region_listbox.delete(0, tk.END)
        for region in self.controller.state.regions:
            self.region_listbox.insert(tk.END, region.name)
        if self.selected_index is not None and self.controller.state.regions:
            self.region_listbox.selection_clear(0, tk.END)
            self.region_listbox.selection_set(self.selected_index)

    def refresh_region_data_view(self) -> None:
        for item in self.region_tree.get_children():
            self.region_tree.delete(item)
        for row in self.controller.region_rows():
            self.region_tree.insert(
                "",
                "end",
                values=(
                    row["name"],
                    f"{row['center_x']:.1f}",
                    f"{row['center_y']:.1f}",
                    f"{row['center_z']:.1f}",
                    f"{row['weight_x']:.3f}",
                    f"{row['weight_y']:.3f}",
                    f"{row['weight_z']:.3f}",
                    f"{row['approach_x']:.1f}",
                    f"{row['approach_y']:.1f}",
                    f"{row['approach_z']:.1f}",
                ),
            )

    def refresh_payload_view(self) -> None:
        self.payload_text.delete("1.0", "end")
        self.payload_text.insert("1.0", json.dumps(self.controller.state.last_result_payload, indent=2, ensure_ascii=False))

    def refresh_summary(self) -> None:
        self.summary_text.delete("1.0", "end")
        dims = self.controller.state.bin_dimensions
        counts = self.controller.region_load_counts()
        if self.metric_regions is not None:
            self.metric_regions.configure(text=str(len(self.controller.state.regions)))
        if self.metric_picks is not None:
            self.metric_picks.configure(text=str(len(self.controller.state.picks)))
        if self.metric_mode is not None:
            self.metric_mode.configure(text=self.auto_generation_mode.get())

        lines = [
            f"Bin [mm]: X={dims.x:.1f} Y={dims.y:.1f} Z={dims.z:.1f}",
            f"Regions: {len(self.controller.state.regions)}",
            f"Simulated/imported picks: {len(self.controller.state.picks)}",
            f"Generation mode: {self.auto_generation_mode.get()}",
            f"Balance strength: {float(self.auto_balance_strength.get()):.2f}",
            f"Last operation: {self.controller.state.last_operation_name}",
            "",
            "Model: implicit quadratic surfaces",
            "J_i = wx*(x-cx)^2 + wy*(y-cy)^2 + wz*(z-cz)^2",
            "",
        ]

        for index, region in enumerate(self.controller.state.regions):
            center = region.center
            weights = region.weights
            approach = region.approach
            lines.append(f"{region.name}:")
            lines.append(f"  Center    = ({center.x:.1f}, {center.y:.1f}, {center.z:.1f})")
            lines.append(f"  Weights   = ({weights.x:.3f}, {weights.y:.3f}, {weights.z:.3f})")
            lines.append(
                f"  Approach  = ({approach.x:.1f}, {approach.y:.1f}, {approach.z:.1f}) | "
                f"R=({approach.rx:.1f}, {approach.ry:.1f}, {approach.rz:.1f})"
            )
            if self.controller.state.picks:
                pct = 100 * counts[index] / max(1, len(self.controller.state.picks))
                lines.append(f"  Picks     = {counts[index]} ({pct:.2f}%)")
            lines.append("")

        try:
            target_loads = (
                self.controller.region_service.parse_target_loads(self.auto_target_loads.get(), len(self.controller.state.regions))
                if self.controller.state.regions
                else None
            )
        except Exception:
            target_loads = None
        if target_loads is not None:
            lines.append("Target load profile: " + ", ".join(f"{100*v:.1f}%" for v in target_loads))
            lines.append("")
        if not SKIMAGE_OK:
            lines.append("WARNING: scikit-image is not available.")
        if not PLOTLY_OK:
            lines.append("WARNING: plotly is not available.")

        self.summary_text.insert("1.0", "\n".join(lines))

    def refresh_from_state(self) -> None:
        """Pull application state into the UI.

        This is the inverse of the sync helpers above. It is called after any use
        case mutates the state so the screen always reflects the authoritative
        application model.
        """
        state = self.controller.state
        self.bin_x.set(state.bin_dimensions.x)
        self.bin_y.set(state.bin_dimensions.y)
        self.bin_z.set(state.bin_dimensions.z)
        self.selected_index = state.selected_index

        self.auto_region_count.set(state.auto_generation.region_count)
        self.auto_init_mode.set(state.auto_generation.init_mode)
        self.auto_generation_mode.set(state.auto_generation.generation_mode)
        self.auto_balance_strength.set(state.auto_generation.balance_strength)
        self.auto_target_loads.set(state.auto_generation.target_loads_raw)
        self.layer_count_var.set(state.auto_generation.layer_count)
        self.auto_k_min.set(state.auto_generation.ideal_k_min)
        self.auto_k_max.set(state.auto_generation.ideal_k_max)

        self.sim_n.set(state.simulation.count)
        self.sim_seed.set(state.simulation.seed)
        self.sim_mode.set(state.simulation.mode)

        self.refresh_region_list()
        self.load_region_editor()
        self.refresh_summary()
        self.refresh_region_data_view()
        self.refresh_payload_view()
