from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

import numpy as np

from inpicker.domain.entities import Region


class RegionClassifier:
    """Pure domain service responsible for scoring and region selection."""

    @staticmethod
    def cost(point: Sequence[float], region: Region) -> float:
        x, y, z = point
        c = region.center
        w = region.weights
        return w.x * (x - c.x) ** 2 + w.y * (y - c.y) ** 2 + w.z * (z - c.z) ** 2

    @classmethod
    def classify(cls, point: Sequence[float], regions: Sequence[Region]) -> Tuple[Optional[int], List[float]]:
        costs = [cls.cost(point, region) for region in regions]
        idx = int(np.argmin(costs)) if costs else None
        return idx, costs
