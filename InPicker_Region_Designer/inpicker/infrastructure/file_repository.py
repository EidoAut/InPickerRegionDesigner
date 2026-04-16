
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from inpicker.application.mapper import StateMapper
from inpicker.domain.entities import AppState, BinDimensions


class FileRepository:
    def read_csv_points(self, path: str) -> np.ndarray:
        return np.genfromtxt(path, delimiter=',', names=True)

    def save_configuration(self, path: str, state: AppState) -> None:
        data = {
            'bin_dimensions_mm': state.bin_dimensions.to_dict(),
            'classification_model': 'implicit_quadratic_surfaces',
            'regions': [region.to_dict() for region in state.regions],
            'result_payload': state.last_result_payload,
        }
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)

    def load_configuration(self, path: str, state: AppState) -> None:
        with open(path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        state.bin_dimensions = BinDimensions(**data.get('bin_dimensions_mm', state.bin_dimensions.to_dict()))
        state.regions = [StateMapper.region_from_dict(item) for item in data.get('regions', [])]
        state.last_result_payload = data.get('result_payload', state.last_result_payload)
        state.last_operation_name = 'load_json'
        state.selected_index = 0 if state.regions else None

    def export_payload(self, path: str, payload: Dict[str, Any]) -> None:
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)

    def export_regions_csv(self, path: str, rows: List[Dict[str, Any]]) -> None:
        with open(path, 'w', newline='', encoding='utf-8') as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
