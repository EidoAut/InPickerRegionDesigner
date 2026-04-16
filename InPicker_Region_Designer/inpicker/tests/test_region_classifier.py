from inpicker.domain.entities import Approach, Region, Vector3
from inpicker.domain.services import RegionClassifier


def test_region_classifier_prefers_nearest_weighted_region():
    regions = [
        Region('A', Vector3(0, 0, 0), Vector3(1, 1, 1), Approach(0, 0, 0)),
        Region('B', Vector3(10, 0, 0), Vector3(1, 1, 1), Approach(10, 0, 0)),
    ]
    idx, costs = RegionClassifier.classify((2, 0, 0), regions)
    assert idx == 0
    assert costs[0] < costs[1]
