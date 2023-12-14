from bleak.uuids import normalize_uuid_16, uuid16_dict


uuid16_lookup = {v: normalize_uuid_16(k) for k, v in uuid16_dict.items()}

# Commonly known BLE characteristics
SYSTEM_ID_UUID = uuid16_lookup["System ID"]

# Device-specific BLE characteristics
COMMAND_UUID = normalize_uuid_16(0xFFE9)
STATE_UUID = normalize_uuid_16(0xFFE4)

# First byte for both Commands and State
PREAMBLE = 0b10100101
