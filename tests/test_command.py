from binascii import unhexlify
from hpa250b_ble import Command


def test_command():
    assert (
        unhexlify("a501000000000000000000000000000000000000")
        == Command().toggle_power().bytes
    )

    assert (
        unhexlify("a504000000000000000000000000000000000000")
        == Command().toggle_general().bytes
    )

    assert (
        unhexlify("a520000000000000000000000000000000000000")
        == Command().toggle_auto_voc().bytes
    )

    assert (
        unhexlify("a500080000000000000000000000000000000000")
        == Command().toggle_auto_pollen().bytes
    )

    assert (
        unhexlify("a500010000000000000000000000000000000000")
        == Command().timer_up().bytes
    )

    assert (
        unhexlify("a5200e0000000000000000000000000000000000")
        == Command()
        .cycle_light()
        .timer_down()
        .toggle_auto_pollen()
        .toggle_auto_voc()
        .bytes
    )


def test_equality():
    assert Command() == Command()
    assert Command().toggle_power() == Command().toggle_power()
    assert Command().timer_up() == Command().timer_up()
