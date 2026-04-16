from inpicker.application.bootstrap import build_controller


def test_controller_bootstrap_creates_four_regions():
    controller = build_controller()
    controller.bootstrap()
    assert len(controller.state.regions) == 4
    assert controller.state.last_operation_name == 'startup'
