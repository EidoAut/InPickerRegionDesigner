
from __future__ import annotations

from typing import Any, Dict, Iterable, List

from inpicker.domain.entities import (
    AppState,
    Approach,
    AutoGenerationConfig,
    BinDimensions,
    PickPoint,
    Region,
    SimulationConfig,
    Vector3,
)


class StateMapper:
    @staticmethod
    def region_from_dict(data: Dict[str, Any]) -> Region:
        return Region(
            name=data['name'],
            center=Vector3(**data['center']),
            weights=Vector3(**data['weights']),
            approach=Approach(**data['approach']),
        )

    @staticmethod
    def region_to_dict(region: Region) -> Dict[str, Any]:
        return region.to_dict()

    @staticmethod
    def pick_from_dict(data: Dict[str, Any]) -> PickPoint:
        return PickPoint(
            x=float(data['x']),
            y=float(data['y']),
            z=float(data['z']),
            region=data.get('region'),
        )

    @staticmethod
    def pick_to_dict(pick: PickPoint) -> Dict[str, Any]:
        return pick.to_dict()

    @classmethod
    def state_to_legacy_dict(cls, state: AppState) -> Dict[str, Any]:
        return {
            'bin_dims': state.bin_dimensions.to_dict(),
            'regions': [cls.region_to_dict(r) for r in state.regions],
            'sim_points': [cls.pick_to_dict(p) for p in state.picks],
            'selected_index': state.selected_index,
            'last_result_payload': state.last_result_payload,
            'last_operation_name': state.last_operation_name,
            'auto': {
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
        }

    @classmethod
    def state_from_legacy_dict(cls, data: Dict[str, Any]) -> AppState:
        auto = data.get('auto', {})
        simulation = data.get('simulation', {})
        return AppState(
            bin_dimensions=BinDimensions(**data.get('bin_dims', {'x': 600.0, 'y': 400.0, 'z': 300.0})),
            regions=[cls.region_from_dict(r) for r in data.get('regions', [])],
            picks=[cls.pick_from_dict(p) for p in data.get('sim_points', [])],
            selected_index=data.get('selected_index'),
            last_result_payload=data.get('last_result_payload', {}),
            last_operation_name=data.get('last_operation_name', 'startup'),
            auto_generation=AutoGenerationConfig(
                region_count=int(auto.get('region_count', 4)),
                init_mode=auto.get('init_mode', 'from_picks'),
                generation_mode=auto.get('generation_mode', 'smart'),
                balance_strength=float(auto.get('balance_strength', 0.35)),
                target_loads_raw=str(auto.get('target_loads_raw', '')),
                layer_count=int(auto.get('layer_count', 2)),
                ideal_k_min=int(auto.get('ideal_k_min', 2)),
                ideal_k_max=int(auto.get('ideal_k_max', 10)),
            ),
            simulation=SimulationConfig(
                count=int(simulation.get('count', 1000)),
                seed=int(simulation.get('seed', 42)),
                mode=simulation.get('mode', 'uniform'),
            ),
        )
