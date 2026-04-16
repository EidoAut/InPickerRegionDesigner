
from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from inpicker.domain.entities import AppState, BinDimensions, PickPoint, Region, Vector3, Approach
from inpicker.domain.exceptions import ValidationError
from inpicker.domain.services import RegionClassifier


class RegionDesignService:
    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed

    def create_region(self, bin_dims: BinDimensions, name: str, cx: float, cy: float, cz: float, wx: float, wy: float, wz: float) -> Region:
        return Region(
            name=name,
            center=Vector3(float(cx), float(cy), float(cz)),
            weights=Vector3(float(wx), float(wy), float(wz)),
            approach=Approach(float(cx), float(cy), float(min(bin_dims.z, cz + 80.0))),
        )

    def cost(self, point: Sequence[float], region: Region) -> float:
        return RegionClassifier.cost(point, region)

    def classify(self, point: Sequence[float], regions: Sequence[Region]) -> Tuple[Optional[int], List[float]]:
        return RegionClassifier.classify(point, regions)

    def region_load_counts(self, state: AppState) -> List[int]:
        counts = [0] * len(state.regions)
        for pick in state.picks:
            idx = pick.region
            if idx is not None and 0 <= idx < len(counts):
                counts[idx] += 1
        return counts

    def serialize_regions_for_export(self, state: AppState) -> List[Dict[str, Any]]:
        counts = self.region_load_counts(state)
        total = max(1, len(state.picks))
        rows: List[Dict[str, Any]] = []
        for i, region in enumerate(state.regions):
            c = region.center
            w = region.weights
            a = region.approach
            rows.append({
                'index': i,
                'name': region.name,
                'center_x': round(float(c.x), 6),
                'center_y': round(float(c.y), 6),
                'center_z': round(float(c.z), 6),
                'weight_x': round(float(w.x), 6),
                'weight_y': round(float(w.y), 6),
                'weight_z': round(float(w.z), 6),
                'approach_x': round(float(a.x), 6),
                'approach_y': round(float(a.y), 6),
                'approach_z': round(float(a.z), 6),
                'approach_rx': round(float(a.rx), 6),
                'approach_ry': round(float(a.ry), 6),
                'approach_rz': round(float(a.rz), 6),
                'pick_count': counts[i] if i < len(counts) else 0,
                'pick_percentage': round((100.0 * counts[i] / total) if i < len(counts) and state.picks else 0.0, 4),
            })
        return rows

    def build_result_payload(self, state: AppState, operation_name: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        extra = extra or {}
        payload = {
            'timestamp': datetime.now().isoformat(timespec='seconds'),
            'operation': operation_name,
            'bin_dimensions_mm': state.bin_dimensions.to_dict(),
            'region_count': len(state.regions),
            'pick_count': len(state.picks),
            'generation_mode': state.auto_generation.generation_mode,
            'auto_parameters': {
                'region_count_requested': int(state.auto_generation.region_count),
                'seed_strategy': state.auto_generation.init_mode,
                'layer_count': int(state.auto_generation.layer_count),
                'balance_strength': float(state.auto_generation.balance_strength),
                'target_load_percentages_raw': state.auto_generation.target_loads_raw.strip(),
                'ideal_k_range': [int(state.auto_generation.ideal_k_min), int(state.auto_generation.ideal_k_max)],
            },
            'regions': [region.to_dict() for region in state.regions],
            'region_rows': self.serialize_regions_for_export(state),
        }
        payload.update(extra)
        return payload

    def update_state_payload(self, state: AppState, operation_name: str, extra: Optional[Dict[str, Any]] = None) -> None:
        state.last_operation_name = operation_name
        state.last_result_payload = self.build_result_payload(state, operation_name, extra)

    def validate_bin_dimensions(self, x: float, y: float, z: float) -> BinDimensions:
        if min(x, y, z) <= 0:
            raise ValidationError('Invalid bin dimensions.')
        return BinDimensions(float(x), float(y), float(z))

    def apply_bin_dimensions(self, state: AppState, x: float, y: float, z: float) -> None:
        state.bin_dimensions = self.validate_bin_dimensions(x, y, z)
        self._clamp_regions_to_bin(state)
        self.reclassify_picks(state)
        self.update_state_payload(state, 'apply_bin_dimensions')

    def _is_within_bin(self, dims: BinDimensions, point: Sequence[float], allow_boundary: bool = True) -> bool:
        x, y, z = map(float, point)
        if allow_boundary:
            return 0.0 <= x <= dims.x and 0.0 <= y <= dims.y and 0.0 <= z <= dims.z
        return 0.0 < x < dims.x and 0.0 < y < dims.y and 0.0 < z < dims.z

    def validate_point_within_bin(self, state: AppState, point: Sequence[float], allow_boundary: bool = True, label: str = 'Point') -> None:
        if not self._is_within_bin(state.bin_dimensions, point, allow_boundary=allow_boundary):
            dims = state.bin_dimensions
            raise ValidationError(
                f"{label} must be inside the bin bounds: 0<=x<={dims.x:.3f}, 0<=y<={dims.y:.3f}, 0<=z<={dims.z:.3f}."
            )

    def _clamp_regions_to_bin(self, state: AppState) -> None:
        dims = state.bin_dimensions
        for region in state.regions:
            region.center = Vector3(
                min(max(float(region.center.x), 0.0), dims.x),
                min(max(float(region.center.y), 0.0), dims.y),
                min(max(float(region.center.z), 0.0), dims.z),
            )
            region.approach = Approach(
                min(max(float(region.approach.x), 0.0), dims.x),
                min(max(float(region.approach.y), 0.0), dims.y),
                min(max(float(region.approach.z), 0.0), dims.z),
                float(region.approach.rx),
                float(region.approach.ry),
                float(region.approach.rz),
            )

    def default_regions(self, bin_dims: BinDimensions, count: int) -> List[Region]:
        x, y, z = bin_dims.x, bin_dims.y, bin_dims.z
        if count == 4:
            specs = [
                ('R1', x * 0.25, y * 0.25, z * 0.50, 1.0, 1.0, 1.15),
                ('R2', x * 0.75, y * 0.25, z * 0.50, 1.0, 1.0, 1.15),
                ('R3', x * 0.25, y * 0.75, z * 0.50, 1.0, 1.0, 1.15),
                ('R4', x * 0.75, y * 0.75, z * 0.50, 1.0, 1.0, 1.15),
            ]
            return [self.create_region(bin_dims, *spec) for spec in specs]
        if count == 8:
            regions = []
            idx = 1
            for zz in (0.30, 0.70):
                for yy in (0.25, 0.75):
                    for xx in (0.25, 0.75):
                        regions.append(self.create_region(bin_dims, f'R{idx}', x * xx, y * yy, z * zz, 1.0, 1.0, 1.35))
                        idx += 1
            return regions
        raise ValidationError(f'Unsupported default region count: {count}')

    def set_default_regions(self, state: AppState, count: int) -> None:
        state.regions = self.default_regions(state.bin_dimensions, count)
        state.selected_index = 0 if state.regions else None
        self.update_state_payload(state, f'auto_generate_{count}_regions')

    def add_region(self, state: AppState) -> None:
        dims = state.bin_dimensions
        state.regions.append(self.create_region(dims, f'R{len(state.regions)+1}', dims.x/2, dims.y/2, dims.z/2, 1.0, 1.0, 1.0))
        state.selected_index = len(state.regions) - 1
        self.update_state_payload(state, 'add_region')

    def duplicate_region(self, state: AppState) -> None:
        if state.selected_index is None:
            return
        original = state.regions[state.selected_index]
        clone = Region(
            name=f'{original.name}_copy',
            center=Vector3(original.center.x, original.center.y, original.center.z),
            weights=Vector3(original.weights.x, original.weights.y, original.weights.z),
            approach=Approach(original.approach.x, original.approach.y, original.approach.z, original.approach.rx, original.approach.ry, original.approach.rz),
        )
        state.regions.append(clone)
        state.selected_index = len(state.regions) - 1
        self.update_state_payload(state, 'duplicate_region')

    def delete_region(self, state: AppState) -> None:
        if state.selected_index is None:
            return
        del state.regions[state.selected_index]
        state.selected_index = 0 if state.regions else None
        self.update_state_payload(state, 'delete_region')

    def update_region(self, state: AppState, index: int, payload: Dict[str, Any]) -> None:
        if index < 0 or index >= len(state.regions):
            raise ValidationError('Invalid region selection.')
        region = state.regions[index]
        region.name = payload.get('name', '').strip() or region.name
        center = (float(payload['center']['x']), float(payload['center']['y']), float(payload['center']['z']))
        approach = (float(payload['approach']['x']), float(payload['approach']['y']), float(payload['approach']['z']))
        self.validate_point_within_bin(state, center, allow_boundary=True, label='Region center')
        self.validate_point_within_bin(state, approach, allow_boundary=True, label='Region approach')
        region.center = Vector3(*center)
        region.weights = Vector3(max(1e-9, float(payload['weights']['x'])), max(1e-9, float(payload['weights']['y'])), max(1e-9, float(payload['weights']['z'])))
        region.approach = Approach(
            approach[0], approach[1], approach[2],
            float(payload['approach']['rx']), float(payload['approach']['ry']), float(payload['approach']['rz'])
        )
        self.reclassify_picks(state)
        self.update_state_payload(state, 'save_region')

    def parse_target_loads(self, raw: str, k: Optional[int] = None) -> Optional[np.ndarray]:
        raw = raw.strip()
        if not raw:
            return None
        vals = []
        for part in raw.replace(';', ',').split(','):
            part = part.strip()
            if part:
                vals.append(float(part))
        if not vals:
            return None
        arr = np.asarray(vals, dtype=float)
        if np.any(arr < 0):
            raise ValidationError('Target load percentages must be non-negative.')
        s = arr.sum()
        if s <= 0:
            raise ValidationError('Target load percentages must sum to a positive value.')
        arr = arr / s
        if k is not None and len(arr) != int(k):
            raise ValidationError(f'Expected {int(k)} target load values, got {len(arr)}.')
        return arr

    def _grid_centers(self, dims: BinDimensions, k: int) -> np.ndarray:
        bx, by, bz = dims.x, dims.y, dims.z
        gx = max(1, int(np.ceil(k ** (1.0 / 3.0))))
        gy = max(1, int(np.ceil((k / gx) ** 0.5)))
        gz = max(1, int(np.ceil(k / max(1, gx * gy))))
        xs = np.linspace(bx / (2 * gx), bx - bx / (2 * gx), gx)
        ys = np.linspace(by / (2 * gy), by - by / (2 * gy), gy)
        zs = np.linspace(bz / (2 * gz), bz - bz / (2 * gz), gz)
        centers = []
        for zz in zs:
            for yy in ys:
                for xx in xs:
                    centers.append([float(xx), float(yy), float(zz)])
                    if len(centers) >= k:
                        return np.array(centers, dtype=float)
        return np.array(centers, dtype=float)

    def _build_seed_centers(self, dims: BinDimensions, pts: np.ndarray, k: int, init_mode: str = 'from_picks') -> np.ndarray:
        rng = np.random.default_rng(self.random_seed)
        if init_mode == 'from_picks' and len(pts) >= k:
            seed_idx = rng.choice(len(pts), size=k, replace=False)
            return pts[seed_idx].copy()
        return self._grid_centers(dims, k)

    def _assign_points_balanced(self, pts: np.ndarray, centers: np.ndarray, target_loads: Optional[np.ndarray] = None, balance_strength: float = 0.0) -> np.ndarray:
        k = len(centers)
        n = len(pts)
        if k == 0 or n == 0:
            return np.zeros(n, dtype=int)
        d2 = np.sum((pts[:, None, :] - centers[None, :, :]) ** 2, axis=2)
        if target_loads is None:
            target_loads = np.full(k, 1.0 / k, dtype=float)
        else:
            target_loads = np.asarray(target_loads, dtype=float)
            target_loads = np.maximum(target_loads, 1e-9)
            target_loads = target_loads / target_loads.sum()
        target_counts = np.maximum(1.0, target_loads * n)
        counts = np.zeros(k, dtype=float)
        order = np.argsort(np.min(d2, axis=1))
        labels = np.zeros(n, dtype=int)
        scale = float(np.mean(d2) + 1e-9)
        strength = max(0.0, float(balance_strength))
        for idx in order:
            overload = counts / target_counts
            penalty = strength * scale * np.maximum(overload - 1.0, 0.0) ** 2
            score = d2[idx] + penalty
            j = int(np.argmin(score))
            labels[idx] = j
            counts[j] += 1.0
        return labels

    def _estimate_region_from_cluster(self, dims: BinDimensions, name: str, cluster: np.ndarray, center_hint: Optional[np.ndarray] = None, z_bounds: Optional[Tuple[float, float]] = None) -> Region:
        bx, by, bz = dims.x, dims.y, dims.z
        if center_hint is None:
            center = cluster.mean(axis=0) if len(cluster) else np.array([bx/2, by/2, bz/2], dtype=float)
        else:
            center = np.asarray(center_hint, dtype=float)
        if len(cluster) > 1:
            spreads = np.std(cluster, axis=0)
        else:
            spreads = np.array([bx, by, bz], dtype=float) / 6.0
        spreads = np.maximum(spreads, np.array([bx, by, bz], dtype=float) * 0.04)
        inv_var = 1.0 / np.maximum(spreads ** 2, 1e-9)
        inv_var /= max(np.mean(inv_var), 1e-9)
        cx = float(np.clip(center[0], 0, bx))
        cy = float(np.clip(center[1], 0, by))
        cz = float(np.clip(center[2], 0, bz))
        if z_bounds is not None:
            z_lo, z_hi = z_bounds
            cz = float(np.clip(cz, z_lo, z_hi))
        region = self.create_region(dims, name, cx, cy, cz, float(inv_var[0]), float(inv_var[1]), float(inv_var[2]))
        if z_bounds is not None:
            z_lo, z_hi = z_bounds
            region.approach.z = float(np.clip(max(cz, z_hi), 0, bz))
        return region

    def _score_clustering(self, pts: np.ndarray, centers: np.ndarray, labels: np.ndarray, target_loads: Optional[np.ndarray] = None) -> float:
        if len(pts) == 0 or len(centers) == 0:
            return -1e18
        sse = 0.0
        counts = np.zeros(len(centers), dtype=float)
        for i, center in enumerate(centers):
            mask = labels == i
            counts[i] = np.sum(mask)
            if np.any(mask):
                diff = pts[mask] - center
                sse += float(np.sum(diff * diff))
        non_empty = counts > 0
        if np.sum(non_empty) > 1:
            pairwise = np.linalg.norm(centers[non_empty][:, None, :] - centers[non_empty][None, :, :], axis=2)
            pairwise += np.eye(np.sum(non_empty)) * 1e9
            separation = float(np.min(pairwise))
        else:
            separation = 0.0
        if target_loads is None:
            target_loads = np.full(len(centers), 1.0 / len(centers), dtype=float)
        else:
            target_loads = np.asarray(target_loads, dtype=float)
            target_loads = target_loads / max(target_loads.sum(), 1e-9)
        observed = counts / max(len(pts), 1)
        balance_penalty = float(np.mean((observed - target_loads) ** 2))
        complexity_penalty = 0.03 * len(centers)
        return -(sse / max(len(pts), 1)) + 0.25 * separation - 18.0 * balance_penalty - complexity_penalty

    def _fit_regions_from_points(self, dims: BinDimensions, points: np.ndarray, k: int, init_mode: str = 'from_picks', max_iter: int = 25, balance_strength: float = 0.0, target_loads: Optional[np.ndarray] = None, z_bounds: Optional[Tuple[float, float]] = None) -> List[Region]:
        pts = np.asarray(points, dtype=float)
        if pts.ndim != 2 or pts.shape[1] != 3 or len(pts) == 0:
            raise ValidationError('No valid 3D points available.')
        k = max(1, min(int(k), len(pts)))
        rng = np.random.default_rng(self.random_seed)
        centers = self._build_seed_centers(dims, pts, k, init_mode=init_mode)
        labels = np.zeros(len(pts), dtype=int)
        for _ in range(max_iter):
            new_labels = self._assign_points_balanced(pts, centers, target_loads=target_loads, balance_strength=balance_strength)
            if np.array_equal(new_labels, labels):
                break
            labels = new_labels
            for i in range(k):
                mask = labels == i
                if np.any(mask):
                    centers[i] = pts[mask].mean(axis=0)
                else:
                    centers[i] = pts[rng.integers(0, len(pts))]
        regions = []
        for i in range(k):
            mask = labels == i
            cluster = pts[mask] if np.any(mask) else pts
            regions.append(self._estimate_region_from_cluster(dims, f'R{i + 1}', cluster, center_hint=centers[i], z_bounds=z_bounds))
        return regions

    def source_points(self, state: AppState, preferred_k: int = 4) -> Tuple[np.ndarray, str]:
        if state.picks:
            pts = np.array([[p.x, p.y, p.z] for p in state.picks], dtype=float)
            return pts, 'picks'
        dims = state.bin_dimensions
        bx, by, bz = dims.x, dims.y, dims.z
        gx = max(4, int(np.ceil(preferred_k ** (1.0 / 3.0)) * 3))
        gy = max(3, int(np.ceil(gx * by / max(bx, 1.0))))
        gz = max(3, int(np.ceil(gx * bz / max(bx, 1.0))))
        xs = np.linspace(0, bx, gx)
        ys = np.linspace(0, by, gy)
        zs = np.linspace(0, bz, gz)
        X, Y, Z = np.meshgrid(xs, ys, zs, indexing='ij')
        pts = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
        return pts, 'grid'

    def reclassify_picks(self, state: AppState) -> None:
        for pick in state.picks:
            pick.region, _ = self.classify((pick.x, pick.y, pick.z), state.regions)

    def auto_generate_from_data(self, state: AppState) -> str:
        k = int(state.auto_generation.region_count)
        if k < 1:
            raise ValidationError('Region count must be positive.')
        points, source = self.source_points(state, preferred_k=k)
        target_loads = self.parse_target_loads(state.auto_generation.target_loads_raw, k)
        state.regions = self._fit_regions_from_points(state.bin_dimensions, points, k=k, init_mode=state.auto_generation.init_mode, balance_strength=float(state.auto_generation.balance_strength), target_loads=target_loads)
        state.selected_index = 0 if state.regions else None
        self.reclassify_picks(state)
        self.update_state_payload(state, 'auto_generate_regions', {
            'source_points': source,
            'target_loads_normalized': None if target_loads is None else target_loads.tolist(),
        })
        return source

    def auto_generate_by_layers(self, state: AppState) -> Dict[str, Any]:
        total_k = int(state.auto_generation.region_count)
        layer_count = max(1, int(state.auto_generation.layer_count))
        if total_k < 1:
            raise ValidationError('Region count must be positive.')
        points, source = self.source_points(state, preferred_k=total_k)
        dims = state.bin_dimensions
        bx, by, bz = dims.x, dims.y, dims.z
        z_edges = np.linspace(0, bz, layer_count + 1)
        if state.picks:
            hist = []
            for i in range(layer_count):
                lo, hi = z_edges[i], z_edges[i + 1]
                mask = (points[:, 2] >= lo) & ((points[:, 2] <= hi) if i == layer_count - 1 else (points[:, 2] < hi))
                hist.append(int(np.sum(mask)))
            hist = np.asarray(hist, dtype=float)
            if np.sum(hist) <= 0:
                hist = np.ones(layer_count, dtype=float)
        else:
            hist = np.ones(layer_count, dtype=float)
        raw_alloc = hist / hist.sum() * total_k
        alloc = np.maximum(1, np.floor(raw_alloc).astype(int))
        while alloc.sum() < total_k:
            idx = int(np.argmax(raw_alloc - alloc))
            alloc[idx] += 1
        while alloc.sum() > total_k:
            candidates = np.where(alloc > 1)[0]
            if len(candidates) == 0:
                break
            idx = int(candidates[np.argmin(raw_alloc[candidates] - alloc[candidates])])
            alloc[idx] -= 1
        target_loads = self.parse_target_loads(state.auto_generation.target_loads_raw, total_k)
        regions: List[Region] = []
        region_offset = 0
        for layer_idx in range(layer_count):
            lo, hi = z_edges[layer_idx], z_edges[layer_idx + 1]
            mask = (points[:, 2] >= lo) & ((points[:, 2] <= hi) if layer_idx == layer_count - 1 else (points[:, 2] < hi))
            layer_points = points[mask]
            if len(layer_points) == 0:
                z_mid = (lo + hi) / 2.0
                xs = np.linspace(bx * 0.2, bx * 0.8, max(2, alloc[layer_idx]))
                ys = np.linspace(by * 0.2, by * 0.8, max(2, alloc[layer_idx]))
                XX, YY = np.meshgrid(xs, ys, indexing='xy')
                layer_points = np.column_stack([XX.ravel(), YY.ravel(), np.full(XX.size, z_mid)])
            local_targets = None
            if target_loads is not None:
                local_targets = target_loads[region_offset:region_offset + alloc[layer_idx]]
                local_targets = local_targets / max(local_targets.sum(), 1e-9)
            layer_regions = self._fit_regions_from_points(dims, layer_points, k=int(alloc[layer_idx]), init_mode='from_picks' if state.auto_generation.init_mode == 'from_picks' else 'grid', balance_strength=float(state.auto_generation.balance_strength), target_loads=local_targets, z_bounds=(float(lo), float(hi)))
            for j, region in enumerate(layer_regions, start=1):
                region.name = f'L{layer_idx + 1}_R{j}'
                regions.append(region)
            region_offset += int(alloc[layer_idx])
        state.regions = regions
        state.selected_index = 0 if state.regions else None
        self.reclassify_picks(state)
        result = {'source_points': source, 'layer_allocation': alloc.tolist(), 'z_edges': z_edges.tolist()}
        self.update_state_payload(state, 'auto_generate_by_layers', result)
        return result

    def optimize_region_loads(self, state: AppState) -> Dict[str, Any]:
        if len(state.regions) < 1:
            raise ValidationError('Create or detect regions first.')
        k = len(state.regions)
        points, source = self.source_points(state, preferred_k=k)
        target_loads = self.parse_target_loads(state.auto_generation.target_loads_raw, k)
        counts = np.array([1.0 / k] * k, dtype=float) if target_loads is None else target_loads
        state.regions = self._fit_regions_from_points(state.bin_dimensions, points, k=k, init_mode=state.auto_generation.init_mode, balance_strength=max(0.35, float(state.auto_generation.balance_strength)), target_loads=counts)
        state.selected_index = 0 if state.regions else None
        self.reclassify_picks(state)
        result = {'source_points': source, 'target_loads_normalized': counts.tolist()}
        self.update_state_payload(state, 'optimize_region_loads', result)
        return result

    def detect_ideal_region_count(self, state: AppState) -> Dict[str, Any]:
        k_min = int(state.auto_generation.ideal_k_min)
        k_max = int(state.auto_generation.ideal_k_max)
        if k_min < 1 or k_max < k_min:
            raise ValidationError('Invalid K range.')
        points, source = self.source_points(state, preferred_k=max(2, k_max))
        best = None
        score_rows = []
        lines = []
        for k in range(k_min, k_max + 1):
            target_loads = None
            raw = state.auto_generation.target_loads_raw.strip()
            if raw:
                try:
                    target_loads = self.parse_target_loads(raw, k)
                except Exception:
                    target_loads = None
            regions = self._fit_regions_from_points(state.bin_dimensions, points, k=k, init_mode=state.auto_generation.init_mode, balance_strength=float(state.auto_generation.balance_strength), target_loads=target_loads)
            centers = np.array([[r.center.x, r.center.y, r.center.z] for r in regions], dtype=float)
            labels = self._assign_points_balanced(points, centers, target_loads=target_loads, balance_strength=float(state.auto_generation.balance_strength))
            score = self._score_clustering(points, centers, labels, target_loads=target_loads)
            lines.append(f'K={k:>2} | score={score: .4f}')
            score_rows.append({'k': k, 'score': float(score)})
            if best is None or score > best[0]:
                best = (score, k, regions)
        if best is None:
            raise ValidationError('Could not evaluate the requested K range.')
        _, best_k, best_regions = best
        state.auto_generation.region_count = best_k
        state.regions = best_regions
        state.selected_index = 0 if state.regions else None
        self.reclassify_picks(state)
        result = {'source_points': source, 'scores': score_rows, 'selected_k': best_k, 'summary_lines': lines}
        self.update_state_payload(state, 'detect_ideal_region_count', result)
        return result

    def evaluate_point(self, state: AppState, point: Sequence[float]) -> Dict[str, Any]:
        point_xyz = {'x': float(point[0]), 'y': float(point[1]), 'z': float(point[2])}
        in_bin = self._is_within_bin(state.bin_dimensions, point, allow_boundary=True)
        idx, costs = self.classify(point, state.regions)
        if idx is None:
            result = {
                'point': point_xyz,
                'inside_bin': in_bin,
                'selected_region_index': None,
                'selected_region_name': None,
                'message': 'No regions defined.',
                'costs': [],
            }
            self.update_state_payload(state, 'evaluate_point', {'evaluation': result})
            return result
        ranked_costs = sorted(
            ({'region_index': i, 'region': state.regions[i].name, 'cost': float(c)} for i, c in enumerate(costs)),
            key=lambda item: item['cost'],
        )
        winner = ranked_costs[0]
        runner_up = ranked_costs[1] if len(ranked_costs) > 1 else None
        margin = float(runner_up['cost'] - winner['cost']) if runner_up is not None else None
        result = {
            'point': point_xyz,
            'inside_bin': in_bin,
            'selected_region_index': idx,
            'selected_region_name': state.regions[idx].name,
            'belongs_to_region': state.regions[idx].name,
            'selected_region': state.regions[idx].to_dict(),
            'classification_rule': 'The point is assigned to the region with the minimum quadratic cost J_i = wx*(x-cx)^2 + wy*(y-cy)^2 + wz*(z-cz)^2.',
            'winning_cost': float(costs[idx]),
            'runner_up_region_name': runner_up['region'] if runner_up else None,
            'runner_up_cost': runner_up['cost'] if runner_up else None,
            'decision_margin': margin,
            'costs': ranked_costs,
            'message': f"Point belongs to region {state.regions[idx].name}.",
        }
        self.update_state_payload(state, 'evaluate_point', {'evaluation': result})
        return result
