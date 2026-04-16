from __future__ import annotations

import json

import pytest

from inpicker.application.bootstrap import build_controller
from inpicker.domain.exceptions import ValidationError


def test_csv_with_single_row_is_loaded_and_classified(tmp_path):
    csv_path = tmp_path / 'single_pick.csv'
    csv_path.write_text('x,y,z\n10,20,30\n', encoding='utf-8')

    controller = build_controller()
    controller.bootstrap()
    loaded = controller.load_picks_csv(str(csv_path))

    assert loaded == 1
    assert len(controller.state.picks) == 1
    assert controller.state.picks[0].region is not None


def test_csv_without_required_columns_fails(tmp_path):
    csv_path = tmp_path / 'bad.csv'
    csv_path.write_text('a,b,c\n1,2,3\n', encoding='utf-8')

    controller = build_controller()
    controller.bootstrap()
    with pytest.raises(ValidationError):
        controller.load_picks_csv(str(csv_path))


def test_save_and_load_round_trip_persists_extended_state(tmp_path):
    controller = build_controller()
    controller.bootstrap()
    controller.state.auto_generation.target_loads_raw = '40,60'
    controller.state.simulation.count = 123
    controller.state.simulation.seed = 99
    controller.state.simulation.mode = 'bottom_heavy'
    controller.generate_simulated_picks()
    controller.state.selected_index = 2
    controller.evaluate_point((10.0, 20.0, 30.0))

    path = tmp_path / 'project.json'
    controller.save_json(str(path))

    reloaded = build_controller()
    reloaded.bootstrap()
    reloaded.load_json(str(path))

    assert len(reloaded.state.picks) == len(controller.state.picks)
    assert reloaded.state.selected_index == 2
    assert reloaded.state.simulation.count == 123
    assert reloaded.state.simulation.seed == 99
    assert reloaded.state.simulation.mode == 'bottom_heavy'
    assert reloaded.state.last_result_payload['operation'] == 'evaluate_point'


def test_evaluate_point_returns_explicit_assigned_region():
    controller = build_controller()
    controller.bootstrap()

    result = controller.evaluate_point((10.0, 20.0, 30.0))

    assert result['selected_region_name']
    assert result['belongs_to_region'] == result['selected_region_name']
    assert result['inside_bin'] is True
    assert len(result['costs']) == len(controller.state.regions)
