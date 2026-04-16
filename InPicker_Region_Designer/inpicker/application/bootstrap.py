from __future__ import annotations

from dataclasses import dataclass

from inpicker.application.controller import InPickerController
from inpicker.application.ports import ConfigurationRepository, PickPointReader, VisualizationGateway
from inpicker.application.use_cases.pick_workflows import PickWorkflowService
from inpicker.application.use_cases.region_design import RegionDesignService
from inpicker.domain.entities import AppState
from inpicker.infrastructure.csv_pick_reader import CsvPickReader
from inpicker.infrastructure.json_project_repository import JsonProjectRepository
from inpicker.infrastructure.plotly_visualizer import PlotlyVisualizer


@dataclass(slots=True)
class ApplicationContainer:
    state: AppState
    region_service: RegionDesignService
    pick_service: PickWorkflowService
    config_repository: ConfigurationRepository
    pick_reader: PickPointReader
    visualizer: VisualizationGateway


def build_controller(state: AppState | None = None) -> InPickerController:
    state = state or AppState()
    region_service = RegionDesignService()
    pick_service = PickWorkflowService(region_service)
    config_repository = JsonProjectRepository()
    pick_reader = CsvPickReader()
    visualizer = PlotlyVisualizer(region_service)
    return InPickerController(
        state=state,
        region_service=region_service,
        pick_service=pick_service,
        config_repository=config_repository,
        pick_reader=pick_reader,
        visualizer=visualizer,
    )
