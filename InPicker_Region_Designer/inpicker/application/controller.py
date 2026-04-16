from __future__ import annotations

from typing import Any, Dict, Sequence

from inpicker.application.ports import ConfigurationRepository, PickPointReader, VisualizationGateway
from inpicker.application.use_cases.pick_workflows import PickWorkflowService
from inpicker.application.use_cases.region_design import RegionDesignService
from inpicker.domain.entities import AppState
from inpicker.infrastructure.csv_pick_reader import CsvPickReader
from inpicker.infrastructure.json_project_repository import JsonProjectRepository
from inpicker.infrastructure.plotly_visualizer import PlotlyVisualizer


class InPickerController:
    """Application façade for the presentation layer.

    The UI talks only to this controller. Infrastructure dependencies are injected
    behind ports so the application layer does not depend directly on Tkinter.
    """

    def __init__(
        self,
        state: AppState | None = None,
        region_service: RegionDesignService | None = None,
        pick_service: PickWorkflowService | None = None,
        config_repository: ConfigurationRepository | None = None,
        pick_reader: PickPointReader | None = None,
        visualizer: VisualizationGateway | None = None,
    ):
        self.state = state or AppState()
        self.region_service = region_service or RegionDesignService()
        self.pick_service = pick_service or PickWorkflowService(self.region_service)
        self.config_repository = config_repository or JsonProjectRepository()
        self.pick_reader = pick_reader or CsvPickReader()
        self.visualizer = visualizer or PlotlyVisualizer(self.region_service)

    def bootstrap(self) -> None:
        self.region_service.set_default_regions(self.state, 4)
        self.region_service.update_state_payload(self.state, 'startup')

    def apply_bin_dimensions(self, x: float, y: float, z: float) -> None:
        self.region_service.apply_bin_dimensions(self.state, x, y, z)

    def auto_generate_default(self, count: int) -> None:
        self.region_service.set_default_regions(self.state, count)

    def auto_generate_from_data(self) -> str:
        return self.region_service.auto_generate_from_data(self.state)

    def auto_generate_by_layers(self) -> Dict[str, Any]:
        return self.region_service.auto_generate_by_layers(self.state)

    def optimize_region_loads(self) -> Dict[str, Any]:
        return self.region_service.optimize_region_loads(self.state)

    def detect_ideal_region_count(self) -> Dict[str, Any]:
        return self.region_service.detect_ideal_region_count(self.state)

    def add_region(self) -> None:
        self.region_service.add_region(self.state)

    def duplicate_region(self) -> None:
        self.region_service.duplicate_region(self.state)

    def delete_region(self) -> None:
        self.region_service.delete_region(self.state)

    def save_region(self, index: int, payload: Dict[str, Any]) -> None:
        self.region_service.update_region(self.state, index, payload)

    def classify(self, point: Sequence[float]):
        return self.region_service.classify(point, self.state.regions)

    def evaluate_point(self, point: Sequence[float]) -> Dict[str, Any]:
        return self.region_service.evaluate_point(self.state, point)

    def generate_simulated_picks(self) -> int:
        return self.pick_service.generate_simulated_picks(self.state)

    def load_picks_csv(self, path: str) -> int:
        rows = self.pick_reader.read_csv_points(path)
        return self.pick_service.load_csv_points(self.state, rows, path)

    def clear_simulation(self) -> None:
        self.pick_service.clear(self.state)

    def save_json(self, path: str) -> None:
        self.config_repository.save_configuration(path, self.state)

    def load_json(self, path: str) -> None:
        self.config_repository.load_configuration(path, self.state)

    def export_payload(self, path: str) -> None:
        self.config_repository.export_payload(path, self.state.last_result_payload)

    def export_regions_csv(self, path: str) -> None:
        rows = self.region_service.serialize_regions_for_export(self.state)
        self.config_repository.export_regions_csv(path, rows)

    def region_rows(self):
        return self.region_service.serialize_regions_for_export(self.state)

    def region_load_counts(self):
        return self.region_service.region_load_counts(self.state)

    def open_regions_and_picks(self):
        return self.visualizer.open_regions_and_picks(self.state)

    def open_colored_surfaces(self, resolution: int):
        return self.visualizer.open_colored_surfaces(self.state, resolution)
