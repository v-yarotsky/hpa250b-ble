from binascii import unhexlify
from hpa250_ble import State, Preset, VOCLight, Backlight


def test_state_from_bytes():
    assert (
        State.from_bytes(unhexlify("a5000000000000000000000000000000000000"))
        == State.empty()
    )

    assert State.from_bytes(
        unhexlify("a5090000000000000000000000000000000000")
    ) == State(True, Preset.GERM, Backlight.ON, None, None)

    assert State.from_bytes(
        unhexlify("a5210500000000000000000000000000000000")
    ) == State(True, Preset.ALLERGEN, Backlight.DIM, None, None)

    assert State.from_bytes(
        unhexlify("a50705000a0000000000000000000000000000")
    ) == State(True, Preset.AUTO_VOC_POLLEN, Backlight.DIM, VOCLight.AMBER, 10)

    assert State.from_bytes(
        unhexlify("a5030a00120000000000000000000000000000")
    ) == State(True, Preset.AUTO_VOC, Backlight.OFF, VOCLight.RED, 18)


def test_equality():
    assert State.empty() == State.empty()
    assert State(True, Preset.GERM, Backlight.DIM, VOCLight.AMBER, 10) == State(
        True, Preset.GERM, Backlight.DIM, VOCLight.AMBER, 10
    )

    assert State(True, Preset.GERM, Backlight.DIM, VOCLight.GREEN, 10) == State(
        True, Preset.GERM, Backlight.DIM, VOCLight.AMBER, 10
    ), "ignores VOC light"

    assert State(True, Preset.GERM, Backlight.DIM, VOCLight.GREEN, 10) != State(
        True, Preset.GENERAL, Backlight.DIM, VOCLight.GREEN, 10
    )

    assert State(True, Preset.GERM, Backlight.DIM, VOCLight.GREEN, 10) != State(
        True, Preset.GERM, Backlight.ON, VOCLight.GREEN, 10
    )

    assert State(True, Preset.GERM, Backlight.DIM, VOCLight.GREEN, 10) != State(
        True, Preset.GERM, Backlight.DIM, VOCLight.GREEN, 9
    )
