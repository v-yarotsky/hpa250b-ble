from hpa250_ble import State, Preset, Backlight, reconcile

from .virtual import VirtualHPA250B


MAX_RECONCILES = 50


def test_reconcile():
    d = VirtualHPA250B()
    desired_state = State(True, Preset.ALLERGEN, Backlight.DIM, None, 13)

    for _ in range(MAX_RECONCILES):
        cmd = reconcile(d.current_state, desired_state)
        if d.apply_command(cmd) == desired_state:
            break

    assert d.current_state == desired_state
