from __future__ import annotations

import math
import numpy as np

from inpicker.domain.entities import AppState, PickPoint
from inpicker.domain.exceptions import ValidationError
from .region_design import RegionDesignService


class PickWorkflowService:
    def __init__(self, region_service: RegionDesignService):
        self.region_service = region_service

    def generate_simulated_picks(self, state: AppState) -> int:
        n = int(state.simulation.count)
        seed = int(state.simulation.seed)
        mode = state.simulation.mode
        if n <= 0:
            raise ValidationError('Simulation count must be positive.')
        rng = np.random.default_rng(seed)
        dims = state.bin_dimensions
        bx, by, bz = dims.x, dims.y, dims.z
        if mode == 'uniform':
            xs = rng.uniform(0, bx, n)
            ys = rng.uniform(0, by, n)
            zs = rng.uniform(0, bz, n)
        elif mode == 'gaussian_center':
            xs = np.clip(rng.normal(bx / 2, bx / 5, n), 0, bx)
            ys = np.clip(rng.normal(by / 2, by / 5, n), 0, by)
            zs = np.clip(rng.normal(bz / 2, bz / 5, n), 0, bz)
        else:
            xs = rng.uniform(0, bx, n)
            ys = rng.uniform(0, by, n)
            zs = np.clip(rng.exponential(bz / 5, n), 0, bz)
        picks = []
        for x, y, z in zip(xs, ys, zs):
            idx, _ = self.region_service.classify((x, y, z), state.regions)
            picks.append(PickPoint(float(x), float(y), float(z), idx))
        state.picks = picks
        self.region_service.update_state_payload(state, 'generate_simulated_picks', {'simulation_mode': mode, 'seed': seed})
        return len(state.picks)

    def load_csv_points(self, state: AppState, rows: np.ndarray, source_path: str) -> int:
        if not state.regions:
            raise ValidationError('At least one region must exist before importing picks.')
        picks = []
        names = {name.lower(): name for name in (rows.dtype.names or [])}
        for row_number, row in enumerate(rows, start=2):
            try:
                x = float(row[names['x']])
                y = float(row[names['y']])
                z = float(row[names['z']])
            except Exception as exc:
                raise ValidationError(f'Invalid CSV row {row_number}. Expected numeric x,y,z values.') from exc
            if not all(math.isfinite(v) for v in (x, y, z)):
                raise ValidationError(f'Invalid CSV row {row_number}. Coordinates must be finite numbers.')
            self.region_service.validate_point_within_bin(state, (x, y, z), allow_boundary=True)
            idx, _ = self.region_service.classify((x, y, z), state.regions)
            picks.append(PickPoint(x, y, z, idx))
        state.picks = picks
        self.region_service.update_state_payload(state, 'load_picks_csv', {'source_file': source_path})
        return len(state.picks)

    def clear(self, state: AppState) -> None:
        state.picks = []
        self.region_service.update_state_payload(state, 'clear_simulation')
