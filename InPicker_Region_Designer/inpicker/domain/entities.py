
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class BinDimensions:
    x: float = 600.0
    y: float = 400.0
    z: float = 300.0

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass(slots=True)
class Vector3:
    x: float
    y: float
    z: float

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass(slots=True)
class Approach:
    x: float
    y: float
    z: float
    rx: float = 0.0
    ry: float = 0.0
    rz: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass(slots=True)
class Region:
    name: str
    center: Vector3
    weights: Vector3
    approach: Approach

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'center': self.center.to_dict(),
            'weights': self.weights.to_dict(),
            'approach': self.approach.to_dict(),
        }


@dataclass(slots=True)
class PickPoint:
    x: float
    y: float
    z: float
    region: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AutoGenerationConfig:
    region_count: int = 4
    init_mode: str = 'from_picks'
    generation_mode: str = 'smart'
    balance_strength: float = 0.35
    target_loads_raw: str = ''
    layer_count: int = 2
    ideal_k_min: int = 2
    ideal_k_max: int = 10


@dataclass(slots=True)
class SimulationConfig:
    count: int = 1000
    seed: int = 42
    mode: str = 'uniform'


@dataclass(slots=True)
class AppState:
    bin_dimensions: BinDimensions = field(default_factory=BinDimensions)
    regions: List[Region] = field(default_factory=list)
    picks: List[PickPoint] = field(default_factory=list)
    selected_index: Optional[int] = None
    last_result_payload: Dict[str, Any] = field(default_factory=dict)
    last_operation_name: str = 'startup'
    auto_generation: AutoGenerationConfig = field(default_factory=AutoGenerationConfig)
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
