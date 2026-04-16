from __future__ import annotations

import csv
import json
from typing import Any, Dict, List

from inpicker.application.mapper import StateMapper
from inpicker.domain.entities import AppState, BinDimensions


class JsonProjectRepository:
    """Infrastructure adapter for project persistence and exports."""

    def save_configuration(self, path: str, state: AppState) -> None:
        data = {
            'bin_dimensions_mm': state.bin_dimensions.to_dict(),
            'classification_model': 'implicit_quadratic_surfaces',
            'regions': [region.to_dict() for region in state.regions],
            'picks': [StateMapper.pick_to_dict(pick) for pick in state.picks],
            'selected_index': state.selected_index,
            'last_operation_name': state.last_operation_name,
            'auto_generation': {
                'region_count': state.auto_generation.region_count,
                'init_mode': state.auto_generation.init_mode,
                'generation_mode': state.auto_generation.generation_mode,
                'balance_strength': state.auto_generation.balance_strength,
                'target_loads_raw': state.auto_generation.target_loads_raw,
                'layer_count': state.auto_generation.layer_count,
                'ideal_k_min': state.auto_generation.ideal_k_min,
                'ideal_k_max': state.auto_generation.ideal_k_max,
            },
            'simulation': {
                'count': state.simulation.count,
                'seed': state.simulation.seed,
                'mode': state.simulation.mode,
            },
            'result_payload': state.last_result_payload,
            'legacy_state': StateMapper.state_to_legacy_dict(state),
        }
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)

    def load_configuration(self, path: str, state: AppState) -> None:
        with open(path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        if 'legacy_state' in data:
            loaded = StateMapper.state_from_legacy_dict(data['legacy_state'])
            state.bin_dimensions = loaded.bin_dimensions
            state.regions = loaded.regions
            state.picks = loaded.picks
            state.selected_index = loaded.selected_index
            state.last_result_payload = loaded.last_result_payload
            state.last_operation_name = 'load_json'
            state.auto_generation = loaded.auto_generation
            state.simulation = loaded.simulation
            return
        state.bin_dimensions = BinDimensions(**data.get('bin_dimensions_mm', state.bin_dimensions.to_dict()))
        state.regions = [StateMapper.region_from_dict(item) for item in data.get('regions', [])]
        state.picks = [StateMapper.pick_from_dict(item) for item in data.get('picks', [])]
        state.last_result_payload = data.get('result_payload', state.last_result_payload)
        state.last_operation_name = data.get('last_operation_name', 'load_json')
        state.selected_index = data.get('selected_index', 0 if state.regions else None)

        auto = data.get('auto_generation', {})
        state.auto_generation.region_count = int(auto.get('region_count', state.auto_generation.region_count))
        state.auto_generation.init_mode = auto.get('init_mode', state.auto_generation.init_mode)
        state.auto_generation.generation_mode = auto.get('generation_mode', state.auto_generation.generation_mode)
        state.auto_generation.balance_strength = float(auto.get('balance_strength', state.auto_generation.balance_strength))
        state.auto_generation.target_loads_raw = str(auto.get('target_loads_raw', state.auto_generation.target_loads_raw))
        state.auto_generation.layer_count = int(auto.get('layer_count', state.auto_generation.layer_count))
        state.auto_generation.ideal_k_min = int(auto.get('ideal_k_min', state.auto_generation.ideal_k_min))
        state.auto_generation.ideal_k_max = int(auto.get('ideal_k_max', state.auto_generation.ideal_k_max))

        simulation = data.get('simulation', {})
        state.simulation.count = int(simulation.get('count', state.simulation.count))
        state.simulation.seed = int(simulation.get('seed', state.simulation.seed))
        state.simulation.mode = simulation.get('mode', state.simulation.mode)
        if state.selected_index is None and state.regions:
            state.selected_index = 0

    def export_payload(self, path: str, payload: Dict[str, Any]) -> None:
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)

    def export_regions_csv(self, path: str, rows: List[Dict[str, Any]]) -> None:
        if not rows:
            raise ValueError('No region rows available to export.')
        with open(path, 'w', newline='', encoding='utf-8') as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
