import pytest
from hpa250_ble import State, Preset, Backlight, reconcile
from .virtual import VirtualHPA250B


MAX_RECONCILES = 50


@pytest.mark.asyncio
async def test_reconcile():
    device = VirtualHPA250B()
    desired_state = State(True, Preset.ALLERGEN, Backlight.DIM, None, 13)

    await reconcile(device, desired_state)

    assert device.current_state.matches_desired_state(desired_state)
