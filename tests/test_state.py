from binascii import unhexlify
from hpa250b_ble import State, Preset, VOCLight, Backlight


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


def test_state_to_bytes():
    assert unhexlify("a5000000000000000000000000000000000000") == State.empty().bytes

    assert (
        unhexlify("a5090000000000000000000000000000000000")
        == State(True, Preset.GERM, Backlight.ON, None, None).bytes
    )

    assert (
        unhexlify("a5210100000000000000000000000000000000")
        == State(True, Preset.ALLERGEN, Backlight.DIM, None, None).bytes
    )

    assert (
        unhexlify("a50705000a0000000000000000000000000000")
        == State(True, Preset.AUTO_VOC_POLLEN, Backlight.DIM, VOCLight.AMBER, 10).bytes
    )

    assert (
        unhexlify("a5030a00120000000000000000000000000000")
        == State(True, Preset.AUTO_VOC, Backlight.OFF, VOCLight.RED, 18).bytes
    )


def test_matches_desired_state():
    assert State.empty().matches_desired_state(State.empty())
    assert State(
        True, Preset.GERM, Backlight.DIM, VOCLight.AMBER, 10
    ).matches_desired_state(State(True, Preset.GERM, Backlight.DIM, VOCLight.AMBER, 10))

    assert State(
        True, Preset.GERM, Backlight.DIM, VOCLight.GREEN, 10
    ).matches_desired_state(
        State(True, Preset.GERM, Backlight.DIM, VOCLight.AMBER, 10)
    ), "ignores VOC light"

    assert not State(
        True, Preset.GERM, Backlight.DIM, VOCLight.GREEN, 10
    ).matches_desired_state(
        State(True, Preset.GENERAL, Backlight.DIM, VOCLight.GREEN, 10)
    )

    assert not State(
        True, Preset.GERM, Backlight.DIM, VOCLight.GREEN, 10
    ).matches_desired_state(State(True, Preset.GERM, Backlight.ON, VOCLight.GREEN, 10))

    assert not State(
        True, Preset.GERM, Backlight.DIM, VOCLight.GREEN, 10
    ).matches_desired_state(State(True, Preset.GERM, Backlight.DIM, VOCLight.GREEN, 9))
