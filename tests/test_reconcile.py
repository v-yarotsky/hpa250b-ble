from hpa250_ble import State, Preset, Backlight, reconcile

from .virtual import VirtualHPA250B


MAX_RECONCILES = 50


def test_reconcile():
    device = VirtualHPA250B()
    desired_state = State(True, Preset.ALLERGEN, Backlight.DIM, None, 13)

    for _ in range(MAX_RECONCILES):
        cmd = reconcile(device.current_state, desired_state)
        device.apply_command(cmd)
        if device.current_state.matches_desired_state(desired_state):
            break

    assert device.current_state.matches_desired_state(desired_state)
