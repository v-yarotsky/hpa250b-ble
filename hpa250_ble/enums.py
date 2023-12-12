from enum import Enum


class Preset(Enum):
    OFF = "off"
    GERM = "germ"
    GENERAL = "general"
    ALLERGEN = "allergen"
    TURBO = "turbo"
    AUTO_VOC = "auto-voc"
    AUTO_POLLEN = "auto-pollen"
    AUTO_VOC_POLLEN = "auto-voc-and-pollen"

    def toJSON(self):
        return str(self)


class Backlight(Enum):
    OFF = "off"
    DIM = "dim"
    ON = "on"

    @classmethod
    def from_byte(cls, b: int) -> "Backlight":
        backlight = b & 0b11  # last 2 bits
        return {
            0: Backlight.ON,
            1: Backlight.DIM,
            2: Backlight.OFF,
        }[backlight]

    @classmethod
    def from_int(cls, n: int) -> "Backlight":
        return {
            0: Backlight.ON,
            1: Backlight.DIM,
            2: Backlight.OFF,
        }[n]

    def toJSON(self):
        return str(self)


class VOCLight(Enum):
    GREEN = "green"
    AMBER = "amber"
    RED = "red"

    @classmethod
    def from_byte(cls, b: int) -> "VOCLight":
        voc = b >> 2  # first 6 bits
        return {
            0: VOCLight.GREEN,
            1: VOCLight.AMBER,
            2: VOCLight.RED,
        }[voc]

    @classmethod
    def from_int(cls, n: int) -> "VOCLight":
        return {
            0: VOCLight.GREEN,
            4: VOCLight.AMBER,
            8: VOCLight.RED,
        }[n]

    def toJSON(self):
        return str(self)
