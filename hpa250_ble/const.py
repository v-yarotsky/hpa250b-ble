from bleak.uuids import normalize_uuid_16, uuid16_dict


uuid16_lookup = {v: normalize_uuid_16(k) for k, v in uuid16_dict.items()}

# Commonly known BLE characteristics
SYSTEM_ID_UUID = uuid16_lookup["System ID"]
MODEL_NBR_UUID = uuid16_lookup["Model Number String"]
DEVICE_NAME_UUID = uuid16_lookup["Device Name"]
MANUFACTURER_NAME_UUID = uuid16_lookup["Manufacturer Name String"]
PNP_ID_UUID = uuid16_lookup["PnP ID"]

# Device-specific BLE characteristics
COMMAND_UUID = normalize_uuid_16(0xFFE9)
STATE_UUID = normalize_uuid_16(0xFFE4)

# byte 1 for both Commands and State
PREAMBLE = 0b10100101


# Commands
## byte 2
COMMAND_TOGGLE_POWER = 1 << 0
COMMAND_TOGGLE_GERM = 1 << 1
COMMAND_TOGGLE_GENERAL = 1 << 2
COMMAND_TOGGLE_ALLERGEN = 1 << 3
COMMAND_TOGGLE_TURBO = 1 << 4
COMMAND_TOGGLE_VOC = 1 << 5

## byte 3
COMMAND_TIMER_UP = 1 << 0
COMMAND_TIMER_DOWN = 1 << 1
COMMAND_LIGHT_CYCLE = 1 << 2
COMMAND_TOGGLE_POLLEN = 1 << 3


# State
## byte 2
STATE_OFF = 0
STATE_ON = 1 << 0
STATE_VOC_SET = 1 << 1
STATE_POLLEN_SET = 1 << 2
STATE_GERM = 1 << 3
STATE_GENERAL = 1 << 4
STATE_ALLERGEN = 1 << 5
STATE_TURBO = 1 << 6

## byte 3
STATE_BACKLIGHT_FULL = 0
STATE_BACKLIGHT_DIM = 1
STATE_BACKLIGHT_OFF = 2

STATE_VOC_LIGHT_GREEN = 0
STATE_VOC_LIGHT_AMBER = 1
STATE_VOC_LIGHT_RED = 2

# Command
# Command size is 40 bytes
# Can be OR-ed
#
#                  SP
# Toggle         a501000000000000000000000000000000000000  00000001
# Germ           a502000000000000000000000000000000000000  00000010
# General        a504000000000000000000000000000000000000  00000100
# Allergy        a508000000000000000000000000000000000000  00001000
# Toggle Turbo   a510000000000000000000000000000000000000  00010000
# Toggle VOC     a520000000000000000000000000000000000000  00100000

# Timer up       a500010000000000000000000000000000000000  00000001
# Timer down     a500020000000000000000000000000000000000  00000010
# Light cycle    a500040000000000000000000000000000000000  00000100
# Toggle Pollen  a500080000000000000000000000000000000000  00001000

# State
# State size is  38 bytes
#
#                  SPLT  TM
# state off:     a5000000001800000000000000000000000000
# state germ:    a5090000001800000000000000000000000000
# state generic: a5110000001800000000000000000000000000
# state allergy  a5210000001800000000000000000000000000
# turbo on       a5410000001800000000000000000000000000
# auto on:       a5030400001800000000000000000000000000
# alrgy auto on: a5070400001800000000000000000000000000
# lights ful:    a5210400001800000000000000000000000000 - allergy
# lights dim:    a5210500001800000000000000000000000000 - allergy
# lights off:    a5210600001800000000000000000000000000 - allergy
# allergy on:    a5050400001800000000000000000000000000
# timer 01h:     a5070000011800000000000000000000000000
# timer 02h:     a5070000021800000000000000000000000000
# timer 03h:     a5070000031800000000000000000000000000
# timer 04h:     a5070000041800000000000000000000000000
# timer 05h:     a5070000051800000000000000000000000000
# timer 06h:     a5070000061800000000000000000000000000
# timer 07h:     a5070000071800000000000000000000000000
# timer 08h:     a5070000081800000000000000000000000000
# timer 09h:     a5070000091800000000000000000000000000
# timer 10h:     a50700000a1800000000000000000000000000
# timer 11h:     a50700000b1800000000000000000000000000
# timer 12h:     a50700000c1800000000000000000000000000
# timer 13h:     a50700000d1800000000000000000000000000
# timer 14h:     a50700000e1800000000000000000000000000
# timer 15h:     a50700000f1800000000000000000000000000
# timer 16h:     a5070000101800000000000000000000000000
# timer 17h:     a5070000111800000000000000000000000000
# timer 18h:     a5070000121800000000000000000000000000

#                a5030500051800000000000000000000000000 - dim, auto, general
#                a5030100051800000000000000000000000000 - dim, auto, germ

# bit order: <preamble> 0 <turbo set> <allergy set> <generic set> <germ set> <pollen set> <auto set> <power set> <6-bit auto speed spec> <2 bit light spec> <pad byte> <1 byte timer spec>

# Speeds:
# - 00 - off                                 00000000
# - 09 - germ                                00001001
# - 11 - generic                             00010001
# - 21 - allergy                             00100001
# - 41 - turbo                               01000001
# - 03 - voc sensor                          00000011
# - 05 - pollen auto-set                     00000101
# - 07 - voc sensor with pollen auto-set     00000111

# Light:
# - 00 - auto speed germ, light full         00000000
# - 01 - auto speed germ, light dim          00000001
# - 02 - auto speed germ, light full         00000010
# - 03 - auto speed general, light full      00000100
# - 04 - auto speed general, light dim       00000101
# - 05 - auto speed general, light off       00000110
# - 06 - auto speed alelrgen, light full     00001000
# - 07 - auto speed alelrgen, light dim      00001001
# - 08 - auto speed alelrgen, light off      00001010

# Timer:
# - 00 - 0h
# - ..
# - 12 - 18h
