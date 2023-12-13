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


class Backlight(Enum):
    OFF = "off"
    DIM = "dim"
    ON = "on"


class VOCLight(Enum):
    GREEN = "green"
    AMBER = "amber"
    RED = "red"
